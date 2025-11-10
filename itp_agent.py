"""ITP-Princeton Agent - Intent to Proceed Processing Agent.

This agent is specialized for reviewing and approving Intent to Proceed documents
for Princeton mortgage applications.
"""

# ==============================================================================
# DEVELOPMENT MODE CONFIGURATION
# ==============================================================================
# Set USE_LOCAL_COPILOTAGENT=true in .env to use local development version
# Set USE_LOCAL_COPILOTAGENT=false (or omit) to use PyPI version
#
# Local version enables testing unreleased features like:
#   - middleware_config parameter in create_remote_subagent
#   - New Station and Server middleware capabilities
#
# Installation (one-time setup):
#   pip install -e /Users/masoud/Desktop/WORK/DeepCopilotAgent2/baseCopilotAgent
# ==============================================================================

import csv
import io
import os
import sys
import uuid
from pathlib import Path

# Check if we should use local copilotagent
USE_LOCAL = os.getenv("USE_LOCAL_COPILOTAGENT", "false").lower() == "true"

if USE_LOCAL:
    # Add local baseCopilotAgent to path
    local_path = Path(__file__).parent.parent.parent / "baseCopilotAgent" / "src"
    if local_path.exists():
        sys.path.insert(0, str(local_path))
        print(f"🔧 DEV MODE: Using LOCAL copilotagent from {local_path}")
    else:
        print(f"⚠️  LOCAL path not found: {local_path}, falling back to installed version")

from cuteagent import HumanAgent
from langchain.tools import ToolRuntime
from langchain_core.tools import tool
from langgraph.config import get_config

from copilotagent import create_deep_agent, create_remote_subagent

# Verify which version is loaded
import copilotagent
if USE_LOCAL and "baseCopilotAgent" in copilotagent.__file__:
    print(f"✅ Using LOCAL copilotagent: {copilotagent.__file__}")
elif not USE_LOCAL and "site-packages" in copilotagent.__file__:
    print(f"✅ Using PyPI copilotagent: {copilotagent.__file__}")
else:
    print(f"⚠️  Version mismatch - Expected {'LOCAL' if USE_LOCAL else 'PyPI'}, got: {copilotagent.__file__}")


@tool
def filter_borrowers_ready_for_itp(runtime: ToolRuntime) -> str:
    """Filter borrowers who are ready for Intent to Proceed (ITP) processing.
    
    This tool reads the borrower table CSV and filters to find borrowers who have:
    1. A date in the "Document Date R" column
    2. A date in at least one of the "eDisclosure D" columns
    
    These criteria indicate the borrower has completed necessary steps and is ready
    for ITP document processing.
    
    Returns:
        A formatted string with the list of borrowers ready for ITP, including their
        loan numbers and relevant dates.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Log all state keys for debugging
    logger.info(f"=== filter_borrowers_ready_for_itp called ===")
    logger.info(f"All state keys: {list(runtime.state.keys())}")
    
    # Get the CSV content from files state (standard state key)
    files = runtime.state.get("files", {})
    logger.info(f"Files keys: {list(files.keys()) if files else 'None'}")
    
    # Files state stores FileData format: {"content": [list of lines], "created_at": str, "modified_at": str}
    file_data = files.get("/borrower_table.csv") if files else None
    
    if file_data and isinstance(file_data, dict) and "content" in file_data:
        # Convert FileData format to string
        csv_content = "\n".join(file_data["content"])
        logger.info(f"CSV from files (FileData): {len(file_data['content'])} lines, {len(csv_content)} chars")
    else:
        # Try to get from table_csv directly in state (fallback)
        csv_content = runtime.state.get("table_csv")
        logger.info(f"CSV from state directly: {csv_content[:100] if csv_content else 'None'}...")
    
    if not csv_content:
        logger.error("No CSV content found in either files or state!")
        return "Error: No borrower table data found. Please run the cute-linear agent first to extract borrower data."
    
    # Parse CSV with duplicate column name handling
    lines = csv_content.strip().split('\n')
    if len(lines) < 2:
        return "Error: CSV data is empty or malformed."
    
    headers = [h.strip() for h in lines[0].split(',')]
    
    # Find column indices
    borrower_name_idx = headers.index("Borrower Name") if "Borrower Name" in headers else -1
    loan_number_idx = headers.index("Loan Number") if "Loan Number" in headers else -1
    doc_date_r_idx = headers.index("Document Date R") if "Document Date R" in headers else -1
    edisclosure_indices = [i for i, h in enumerate(headers) if h == "eDisclosure D"]
    
    logger.info(f"Found columns - Borrower Name: {borrower_name_idx}, Doc Date R: {doc_date_r_idx}, eDisclosure: {edisclosure_indices}")
    
    ready_borrowers = []
    
    for line in lines[1:]:  # Skip header
        if not line.strip():
            continue
            
        try:
            row_values = next(csv.reader([line]))
        except Exception as e:
            logger.warning(f"Error parsing line: {e}")
            continue
        
        if len(row_values) <= max(borrower_name_idx, loan_number_idx, doc_date_r_idx):
            continue
        
        borrower_name = row_values[borrower_name_idx].strip().strip('"') if borrower_name_idx >= 0 else ""
        loan_number = row_values[loan_number_idx].strip() if loan_number_idx >= 0 else ""
        doc_date_r = row_values[doc_date_r_idx].strip() if doc_date_r_idx >= 0 else ""
        
        # Check eDisclosure columns - need BOTH columns to have dates
        edisclosure_dates = []
        for idx in edisclosure_indices:
            if idx < len(row_values):
                date_val = row_values[idx].strip()
                if date_val and date_val not in ['', '=', ',']:
                    edisclosure_dates.append(date_val)
                else:
                    # Track empty columns too
                    edisclosure_dates.append(None)
        
        # Filter: must have Document Date R AND BOTH eDisclosure D columns filled
        # There should be exactly 2 eDisclosure columns and both must have dates
        has_both_edisclosures = (
            len(edisclosure_dates) == 2 and 
            edisclosure_dates[0] is not None and 
            edisclosure_dates[1] is not None
        )
        
        if doc_date_r and doc_date_r not in ['', '=', ','] and has_both_edisclosures:
            # Filter out None values for display
            valid_edisclosure_dates = [d for d in edisclosure_dates if d is not None]
            ready_borrowers.append({
                "name": borrower_name,
                "loan_number": loan_number,
                "doc_date": doc_date_r,
                "edisclosure_dates": valid_edisclosure_dates
            })
            logger.info(f"Found ready borrower: {borrower_name} (Loan: {loan_number})")
    
    if not ready_borrowers:
        return """No borrowers are currently ready for ITP processing.

Borrowers need ALL THREE dates filled:
1. A date in the "Document Date R" column
2. A date in the FIRST "eDisclosure D" column
3. A date in the SECOND "eDisclosure D" column

Please check the borrower table for status updates."""
    
    # Format response
    result = f"**Found {len(ready_borrowers)} borrower(s) ready for Intent to Proceed (ITP) processing:**\n\n"
    
    for i, borrower in enumerate(ready_borrowers, 1):
        result += f"{i}. **{borrower['name']}**\n"
        result += f"   - Loan Number: {borrower['loan_number']}\n"
        result += f"   - Document Date: {borrower['doc_date']}\n"
        result += f"   - eDisclosure Date(s): {', '.join(borrower['edisclosure_dates'])}\n\n"
    
    result += "These borrowers have completed the necessary documentation steps and are ready for ITP document processing."
    
    return result


@tool
def report_error_to_hitl(
    error_message: str,
    borrower_name: str | None = None,
    loan_number: str | None = None,
) -> str:
    """Report an error to the Human-In-The-Loop (HITL) system for review.
    
    Use this tool whenever ANY subagent or tool fails during processing.
    This sends a C1-R0 report to the HITL system so a human can review and take action.
    
    Common use cases:
    - cute-finish-itp fails to process a borrower's ITP document
    - cute-linear fails to extract borrower data
    - Any other tool or subagent encounters an error
    
    Args:
        error_message: Description of the error that occurred (REQUIRED)
        borrower_name: Full name of the borrower if applicable (e.g., "Stewart, Lindsey Elize")
        loan_number: Loan number if applicable (e.g., "000068825")
        
    Returns:
        Confirmation message that the error was reported to HITL
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Get HITL credentials from environment
    hitl_token = os.getenv("HITL_TOKEN")
    hitl_url = os.getenv(
        "HITL_URL",
        "https://d5x1qrpuf7.execute-api.us-west-1.amazonaws.com/prod/"
    )
    
    if not hitl_token:
        logger.warning("HITL_TOKEN not set - skipping error report")
        identifier = f"{borrower_name} (Loan: {loan_number})" if borrower_name and loan_number else "this error"
        return f"⚠️ HITL_TOKEN not configured. Error for {identifier} was NOT reported to HITL system."
    
    try:
        # Get thread_id from config
        config = get_config()
        thread_id = None
        if config:
            thread_id = config.get("configurable", {}).get("thread_id")
        
        if not thread_id:
            thread_id = str(uuid.uuid4())
            logger.warning(f"No thread_id in config, using generated UUID: {thread_id}")
        
        # Initialize HumanAgent
        human_agent = HumanAgent(HITL_token=hitl_token, HITL_url=hitl_url)
        
        # Note: screenshot_url would need to be passed as a parameter if needed
        # For now, we'll set it to None since we don't have runtime access
        screenshot_url = None
        
        # Prepare state dictionary for C1-R0 error report
        state_dict = {
            "loan_number": loan_number or "UNKNOWN",
            "borrower_name": borrower_name or "UNKNOWN",
            "status": "error",
            "message": error_message,
            "screenshot_url": screenshot_url,
            "report_type": "C1-R0",
            "timestamp": str(uuid.uuid4()),
        }
        
        # Send C1-R0 report to HITL
        identifier = f"{borrower_name} (Loan: {loan_number})" if borrower_name and loan_number else "error"
        logger.info(f"Sending C1-R0 error report for {identifier} to HITL...")
        human_agent.reporting(
            thread_id=str(thread_id),
            thread_state=state_dict,
            report_type="C1-R0"
        )
        
        logger.info("✅ Successfully reported error to HITL")
        return f"✅ Error reported to HITL system for {identifier}. A human reviewer will investigate and take appropriate action."
        
    except Exception as e:
        logger.error(f"Failed to report error to HITL: {e}", exc_info=True)
        identifier = f"{borrower_name} (Loan: {loan_number})" if borrower_name and loan_number else "this error"
        return f"❌ Failed to report error to HITL system: {e}. Error for {identifier} was NOT reported."


# Simple system prompt - detailed workflow guidance is handled by the planner
itp_instructions = """You are an Intent to Proceed (ITP) processor for Princeton mortgage.

Your job is to review and approve ITP documents for mortgage applications. Use the planner to organize your work.

## Your Workflow:
1. Extract borrower data using cute-linear subagent
2. Filter ready borrowers using filter_borrowers_ready_for_itp tool
3. If borrowers are ready: Process each with cute-finish-itp subagent
4. If NO borrowers are ready: Report to user and end

## Available Tools:

### Subagents (via task tool):
- **cute-linear**: Extract borrower data from GUI with screenshots
- **cute-finish-itp**: Complete ITP workflow for a specific borrower (ONLY if they passed the filter)

### Filtering Tool:
- **filter_borrowers_ready_for_itp**: Identifies borrowers ready for ITP by checking if they have:
  - A date in "Document Date R" column
  - Dates in BOTH "eDisclosure D" columns

### Error Reporting Tool:
- **report_error_to_hitl**: Report errors to Human-In-The-Loop (HITL) system
  - Use this whenever ANY tool or subagent fails
  - Include borrower_name and loan_number when available
  - Sends a C1-R0 report for human review

## Important:
- ONLY use cute-finish-itp if the filter tool found ready borrowers
- If no borrowers are ready, present results and END - do not attempt to process
- **CRITICAL**: If ANY tool or subagent fails, ALWAYS use report_error_to_hitl to notify human reviewers
- Keep the user informed at each step"""

# Load local planning prompt
planner_prompt_file = Path(__file__).parent / "planner_prompt.md"
planning_prompt = planner_prompt_file.read_text() if planner_prompt_file.exists() else None

# Define cloud subagents locally (customizable!)
# Get current thread_id to use as station_id for data syncing
def get_current_thread_id():
    """Get current thread_id from LangGraph config."""
    config = get_config()
    if config:
        thread_id = config.get("configurable", {}).get("thread_id")
        if thread_id:
            return thread_id
    return "itp-princeton-default-station"

# Calculate station_id for this agent instance
current_station_id = get_current_thread_id()

cute_linear = create_remote_subagent(
    name="cute-linear",
    url="https://cutelineargraph-ef1ae523c24e51ef94e330929a65833b.us.langgraph.app",
    graph_id="cuteLinearGraph",
    description=(
        "Coordinated Data Extraction Agent - Performs automated GUI data extraction "
        "including navigation, OCR via AWS Textract, and AI-powered name normalization. "
        "Extracts borrower names from GUI interface, sends for human review, and reports "
        "results back. Use this agent when you need to extract borrower names from the "
        "GUI system."
    ),
    middleware_config={
        "station": {
            "variables": ["borrower_names", "reason_code"],
            "station_id": current_station_id  # Explicitly calculated here
        },
        "server": {
            "server_id": "princetonProd",
            "checkpoint": "Home",
            "server_index": 0
        }
    },
)

cute_finish_itp = create_remote_subagent(
    name="cute-finish-itp",
    url="https://cutefinishitp-2d3fcf81a7e55dd09a66354c5c2b567c.us.langgraph.app",
    graph_id="cuteFinishITP",
    description=(
        "Encompass GUI Automation Agent - Executes a 25-step workflow for ITP document "
        "processing including popup detection, form filling, document verification, and "
        "final submission.\n\n"
        "REQUIRED INPUTS:\n"
        "  This agent requires the 'inputs' parameter with borrower information:\n"
        '  inputs={{"borrower_name": "LastName, FirstName MiddleName", "loan_number": "000012345"}}\n\n'
        "Example call:\n"
        "  task(\n"
        '    subagent_type="cute-finish-itp",\n'
        '    description="Complete ITP processing workflow",\n'
        '    inputs={{"borrower_name": "Stewart, Lindsey Elize", "loan_number": "000068825"}}\n'
        "  )"
    ),
    middleware_config={
        "station": {
            "variables": ["borrower_names", "reason_code"],
            "station_id": STATION_ID  # Set via ITP_STATION_ID env var or default
        },
        "server": {
            "server_id": "princetonProd",
            "checkpoint": "Home",
            "server_index": 0
        }
    },
)

# Create the ITP-Princeton agent with cloud subagents and ITP-specific tools
# langgraph.json loads .env before this module executes
agent = create_deep_agent(
    agent_type="ITP-Princeton",
    system_prompt=itp_instructions,
    planning_prompt=planning_prompt,  # Use local planning prompt
    tools=[filter_borrowers_ready_for_itp, report_error_to_hitl],
    subagents=[cute_linear, cute_finish_itp],  # Use local subagent definitions
    # Note: station_thread_id for station syncing will be automatically resolved from:
    # 1. Agent state (if you set state["station_thread_id"])
    # 2. Parent agent's thread_id (automatic fallback)
    # 
    # To use a specific station, invoke agent with:
    # agent.invoke({
    #     "messages": [...],
    #     "station_thread_id": "my-custom-station-id"
    # })
)

# When this agent is invoked without messages, it will present the default message:
# "Let's review and approve Intent to Proceed for Princeton mortgage"
# The user can approve or modify this message before proceeding.

if __name__ == "__main__":
    print("ITP-Princeton Agent created successfully!")
    print("This agent is configured to review and approve Intent to Proceed documents.")
    print()
    print("Default starting message:")
    print("'Let's review and approve Intent to Proceed for Princeton mortgage'")
    print()
    print("To use this agent:")
    print("1. Invoke with no messages to use the default starting message")
    print("2. Or provide a specific application to review")
    print()
    print("Example usage:")
    print('agent.invoke({"messages": []})')
    print('# or')
    print('agent.invoke({"messages": [{"role": "user", "content": "Review the Smith application"}]})')

