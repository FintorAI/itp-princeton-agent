# 🏦 ITP-Princeton Agent

**Intent to Proceed Processing Agent for Princeton Mortgage**

[![LangGraph Cloud](https://img.shields.io/badge/LangGraph-Cloud-blue)](https://smith.langchain.com/)
[![GitHub](https://img.shields.io/badge/GitHub-ITP--Princeton-green)](https://github.com/FintorAI/itp-princeton-agent)

---

## 📋 Overview

This agent automates the review and approval of Intent to Proceed (ITP) documents for Princeton mortgage applications. It follows a structured 3-phase workflow with cloud-based GUI automation.

---

## ✨ Features

- ✅ **Automated Document Review** - Systematically reviews all required fields
- ✅ **Compliance Checking** - Validates against Princeton mortgage policies
- ✅ **GUI Automation** - Integrates with cloud subagents for GUI tasks
- ✅ **Task Tracking** - Built-in todo list for progress management
- ✅ **Custom Planning** - Local `planner_prompt.md` for workflow customization
- ✅ **Default Starting Message** - Presents default message for quick start

---

## 🚀 Quick Start

### Local Development

```bash
cd agents/ITP-Princeton

# Create .env file with API keys
cat > .env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-api03-...
LANGCHAIN_API_KEY=lsv2_pt_...
EOF

# Start dev server
langgraph dev

# Open http://localhost:2024
```

### GitHub Repository

**Repo**: https://github.com/FintorAI/itp-princeton-agent

**Deploy Command:**
```bash
git add .
git commit -m "Update agent"
git push origin main
# → LangGraph Cloud auto-deploys!
```

---

## 🔐 Environment Variables

### Required Variables

**1. ANTHROPIC_API_KEY** ✅ Required
- **Purpose**: Claude Sonnet 4.5 model (main agent LLM)
- **Get from**: https://console.anthropic.com/settings/keys
- **Format**: `sk-ant-api03-...`

**2. LANGCHAIN_API_KEY** ✅ Required
- **Purpose**: Connect to cloud subagents (cute-linear, cute-finish-itp)
- **Get from**: https://smith.langchain.com/ → Settings → API Keys
- **Format**: `lsv2_pt_...`
- **Alternative names**: `LANGSMITH_API_KEY` or `LANGGRAPH_API_KEY`

### Setting Variables

**For Local Development:**
```bash
# Create .env in agent directory
ANTHROPIC_API_KEY=sk-ant-api03-your-key
LANGCHAIN_API_KEY=lsv2_pt_your-key
```

**For LangGraph Cloud:**
1. Go to: https://smith.langchain.com/deployments
2. Select deployment → Environment Variables
3. Add both keys above

---

## 🔄 Agent Workflow

### Phase 1: Data Extraction
Uses `cute-linear` cloud subagent to:
- Navigate Princeton GUI interface
- Capture screenshots
- Extract borrower names and data via OCR
- Save borrower table CSV to filesystem

### Phase 2: Filter Ready Borrowers
Uses `filter_borrowers_ready_for_itp` tool to:
- Read borrower table CSV from filesystem
- Check for required dates:
  - "Document Date R" column must have a date
  - BOTH "eDisclosure D" columns must have dates
- Return list of ready borrowers OR message that none are ready

### Phase 3: Process or Report

**If borrowers ARE ready:**
- Present filtered list to user
- For EACH ready borrower:
  - Use `cute-finish-itp` subagent
  - Complete 25-step ITP workflow in Encompass
  - Verify submission
- Report final completion status

**If NO borrowers are ready:**
- Present requirements to user
- End workflow (do not attempt processing)

---

## 🛠️ Available Tools

### Subagents (via task tool)

**cute-linear**
- Coordinated data extraction from GUI
- Multi-step navigation and OCR
- Human-in-the-loop review
- Returns borrower table CSV

**cute-finish-itp**
- Encompass GUI automation
- 25-step ITP workflow
- Form navigation and filling
- Document submission

### Custom Tool

**filter_borrowers_ready_for_itp**
- Filters borrower table CSV
- Checks document readiness criteria
- Returns ready borrowers or requirements message

### Built-in Tools

- `write_todos` - Plan and track tasks
- `ls` - List files
- `read_file` - Read documents
- `write_file` - Create reports
- `edit_file` - Update files

---

## 📂 File Structure

```
ITP-Princeton/
├── itp_agent.py           # Agent implementation
├── planner_prompt.md      # Custom planning workflow (editable!)
├── requirements.txt       # Dependencies (copilotagent>=0.1.8)
├── langgraph.json         # LangGraph Cloud config
├── .env                   # Environment variables (not in git)
├── .gitignore             # Python + LangGraph ignores
└── README_CONSOLIDATED.md # This file
```

---

## 🎨 Customization

### Edit Planning Workflow

```bash
# Edit the planning prompt
nano planner_prompt.md

# Commit and push
git add planner_prompt.md
git commit -m "Refine ITP workflow phases"
git push origin main

# → LangGraph Cloud auto-deploys with new planning! ✅
```

### Add Custom Subagents

```python
# In itp_agent.py
from copilotagent import create_remote_subagent

# Add custom validator subagent
validator = create_remote_subagent(
    name="compliance-validator",
    url="https://validator.us.langgraph.app",
    graph_id="validatorGraph",
    description="Validates ITP documents for compliance"
)

agent = create_deep_agent(
    agent_type="ITP-Princeton",
    subagents=[
        get_cute_linear_subagent(),
        get_cute_finish_itp_subagent(),
        validator,  # Custom!
    ]
)
```

### Add Custom Tools

```python
from langchain_core.tools import tool

@tool
def validate_loan_amount(amount: float) -> str:
    """Validate loan amount against Princeton limits."""
    # Your validation logic
    return "Valid" if amount <= 5000000 else "Exceeds limit"

agent = create_deep_agent(
    agent_type="ITP-Princeton",
    tools=[filter_borrowers_ready_for_itp, validate_loan_amount],
    ...
)
```

---

## 🌐 LangGraph Cloud Deployment

### Initial Setup

1. **Deploy to GitHub** (already done):
   - Repo: https://github.com/FintorAI/itp-princeton-agent

2. **Connect to LangGraph Cloud**:
   - Go to: https://smith.langchain.com/deployments
   - Click "+ New Deployment"
   - Select: GitHub → FintorAI/itp-princeton-agent
   - Branch: main

3. **Configure Environment Variables**:
   - `ANTHROPIC_API_KEY`
   - `LANGCHAIN_API_KEY`

4. **Deploy**:
   - Click "Submit"
   - Wait ~5 minutes
   - Test in playground!

### Auto-Deploy on Push

After initial setup, any push to GitHub automatically redeploys:

```bash
git add .
git commit -m "Update agent logic"
git push origin main
# → Auto-deploys to LangGraph Cloud! ✅
```

---

## 📊 Dependencies

```txt
copilotagent>=0.1.8      # Core framework (from PyPI)
langchain>=1.0.0         # LangChain framework
langchain-anthropic>=1.0.0  # Claude model
langchain-core>=1.0.0    # LangChain core
langgraph-sdk>=0.1.0     # Cloud subagent connections
```

---

## 💡 Usage Example

```python
from copilotagent import (
    create_deep_agent,
    get_cute_linear_subagent,
    get_cute_finish_itp_subagent,
)
from pathlib import Path

# Load custom planning prompt
planning_prompt = Path("planner_prompt.md").read_text()

# Create agent
agent = create_deep_agent(
    agent_type="ITP-Princeton",
    system_prompt="You are an ITP processor for Princeton mortgage.",
    planning_prompt=planning_prompt,  # Custom workflow!
    tools=[filter_borrowers_ready_for_itp],
    subagents=[
        get_cute_linear_subagent(),
        get_cute_finish_itp_subagent(),
    ],
)

# Invoke with default message
result = agent.invoke({"messages": []})
# Presents: "Let's review and approve Intent to Proceed for Princeton mortgage"

# Or with custom message
result = agent.invoke({
    "messages": [{"role": "user", "content": "Process Smith application"}]
})
```

---

## 🐛 Troubleshooting

### Error: "No module named 'dotenv'"
**Fix**: Update to `copilotagent>=0.1.7`

### Error: "API key environment variable is required"
**Fix**: Ensure `.env` file has `LANGCHAIN_API_KEY`

### Error: "Authentication failed" from cloud subagents
**Fix**: Verify `LANGCHAIN_API_KEY` is valid and has access to subagents

### LangGraph Cloud build fails
**Fix**: Wait 10-15 minutes after publishing new `copilotagent` version (PyPI CDN propagation)

---

## 📚 Related Documentation

- **Base Package**: https://github.com/FintorAI/copilotBase
- **DrawDoc-AWM Agent**: https://github.com/FintorAI/drawdoc-awm-agent
- **Research Agent**: https://github.com/FintorAI/research-agent
- **LangGraph Cloud Docs**: https://docs.langchain.com/langgraph-platform/

---

## ✅ Current Status

- ✅ Deployed to GitHub: https://github.com/FintorAI/itp-princeton-agent
- ✅ Using copilotagent v0.1.8 from PyPI
- ✅ Custom planning prompt: `planner_prompt.md`
- ✅ Cloud subagents integrated
- ✅ Auto-deploy on push enabled

---

**Ready for LangGraph Cloud deployment!** 🚀


