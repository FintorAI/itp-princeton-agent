# ITP-Princeton Agent

Intent to Proceed Processing Agent for Princeton Mortgage

## Overview

This agent is specialized for reviewing and approving Intent to Proceed (ITP) documents for Princeton mortgage applications. It follows a structured workflow to ensure thorough and compliant document review.

## Features

- **Automated Document Review**: Systematically reviews all required fields and information
- **Compliance Checking**: Validates against Princeton mortgage policies
- **Task Tracking**: Uses built-in todo list for progress tracking
- **File System Integration**: Reads documents, writes reports, and maintains review history
- **Default Starting Message**: Automatically presents "Let's review and approve Intent to Proceed for Princeton mortgage" when invoked

## Agent Capabilities

### Document Review Workflow
1. Initial document review
2. Borrower information verification
3. Loan terms validation
4. Compliance check
5. Final approval/rejection decision

### Built-in Tools
- `write_todos`: Plan and track review tasks
- `ls`: List available documents
- `read_file`: Read application documents
- `write_file`: Create review reports
- `edit_file`: Update existing documents
- `task`: Delegate work to specialized subagents

### Cloud Subagents

This agent has access to two specialized cloud subagents for GUI automation:

#### cute-linear
**Coordinated Data Extraction Agent**

Performs automated GUI data extraction including:
- Multi-step GUI navigation
- Screenshot capture and OCR via AWS Textract
- AI-powered name normalization
- Human-in-the-loop review
- Results reporting

Use this subagent when you need to extract borrower names from the GUI system.

#### cute-finish-itp
**Encompass GUI Automation Agent**

Executes a 25-step workflow for ITP document processing including:
- Popup detection and handling
- Form field navigation and filling
- Document verification
- Final document submission
- Screenshot capture for verification

Use this subagent when you need to complete the ITP document processing workflow in the Encompass GUI system.

## Usage

### Basic Usage

```python
from copilotagent import create_deep_agent

# Create the agent
agent = create_deep_agent(
    agent_type="ITP-Princeton",
    system_prompt="Additional custom instructions..."
)

# Use with default starting message
result = agent.invoke({"messages": []})
# Presents: "Let's review and approve Intent to Proceed for Princeton mortgage"

# Or provide specific task
result = agent.invoke({
    "messages": [{"role": "user", "content": "Review the Smith application"}]
})
```

### Running the Example

```bash
cd agent/ITP-Princeton
python itp_agent.py
```

## Configuration

The agent is configured with:
- **Agent Type**: `ITP-Princeton`
- **Default Model**: Claude Sonnet 4.5
- **Planning**: ITP-specific planning prompts
- **Default Message**: "Let's review and approve Intent to Proceed for Princeton mortgage"
- **Cloud Subagents**: cuteLinear and cuteFinishITP (requires `LANGCHAIN_API_KEY` environment variable)

## Workflow Example

When you invoke the agent, it will:

1. **Accept or modify the starting message** (if invoked without messages)
2. **Create a review plan** using the todo list tool
3. **Read the application documents** from the file system
4. **Perform verification checks** on all required information
5. **Document findings** in review reports
6. **Provide approval/rejection recommendation**

## Requirements

- Python 3.11+
- copilotagent package (from PyPI)
- LangChain dependencies (installed with copilotagent)
- langgraph-sdk (for cloud subagents)
- `LANGCHAIN_API_KEY` environment variable (for connecting to cloud subagents)
- `ANTHROPIC_API_KEY` environment variable (for Claude model)

See `requirements.txt` for full list of dependencies.

## Integration

This agent can be integrated into:
- Mortgage processing workflows
- Document management systems
- Compliance tracking systems
- Approval automation pipelines

## Support

For questions or issues with the ITP-Princeton agent, refer to the main CopilotAgent documentation.

