"""ITP-Princeton Agent - Intent to Proceed Processing Agent.

This agent is specialized for reviewing and approving Intent to Proceed documents
for Princeton mortgage applications.
"""

import csv
import io
import os
from pathlib import Path

from langchain.tools import ToolRuntime
from langchain_core.tools import tool

from copilotagent import (
    create_deep_agent,
    get_cute_finish_itp_subagent,
    get_cute_linear_subagent,
)


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

## Important:
- ONLY use cute-finish-itp if the filter tool found ready borrowers
- If no borrowers are ready, present results and END - do not attempt to process
- Keep the user informed at each step"""

# Load local planning prompt
planner_prompt_file = Path(__file__).parent / "planner_prompt.md"
planning_prompt = planner_prompt_file.read_text() if planner_prompt_file.exists() else None

# Create the ITP-Princeton agent with cloud subagents and ITP-specific tools
# langgraph.json loads .env before this module executes
agent = create_deep_agent(
    agent_type="ITP-Princeton",
    system_prompt=itp_instructions,
    planning_prompt=planning_prompt,  # Use local planning prompt
    tools=[filter_borrowers_ready_for_itp],
    subagents=[
        get_cute_linear_subagent(),
        get_cute_finish_itp_subagent(),
    ],
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

