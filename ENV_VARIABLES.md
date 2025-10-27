# 🔐 Environment Variables for ITP-Princeton Agent

## Required Environment Variables

The ITP-Princeton agent requires **2 environment variables** to function:

### 1. ANTHROPIC_API_KEY ✅ Required
**Purpose:** Claude Sonnet 4.5 model (main agent LLM)

**Get it from:** https://console.anthropic.com/settings/keys

**Format:** `sk-ant-api03-...`

**Used for:** All LLM calls made by the agent

### 2. LANGCHAIN_API_KEY ✅ Required
**Purpose:** Connect to cloud-deployed subagents (cute-linear, cute-finish-itp)

**Get it from:** https://smith.langchain.com/ → Settings → API Keys

**Format:** `lsv2_pt_...`

**Used for:** Making API calls to:
- `cute-linear` - Borrower data extraction from GUI
- `cute-finish-itp` - ITP document completion workflow

**Alternative names:** The code accepts any of these:
- `LANGCHAIN_API_KEY` (recommended)
- `LANGSMITH_API_KEY`
- `LANGGRAPH_API_KEY`

---

## 🔧 Setting Up Environment Variables

### For Local Development (langgraph dev)

Create a `.env` file in the agent directory:

```bash
cd /Users/masoud/Desktop/WORK/DeepCopilotAgent2/agents/ITP-Princeton

cat > .env << 'EOF'
# Claude Model API Key
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# LangSmith/LangGraph API Key (for cloud subagents)
LANGCHAIN_API_KEY=lsv2_pt_your-key-here
EOF
```

**Important:** `.env` is in `.gitignore` and will NOT be committed to GitHub

### For LangGraph Cloud Deployment

Configure in the LangSmith dashboard:

1. Go to: https://smith.langchain.com/deployments
2. Select your deployment
3. Go to "Environment Variables" section
4. Add:
   - Key: `ANTHROPIC_API_KEY`, Value: `sk-ant-api03-...`
   - Key: `LANGCHAIN_API_KEY`, Value: `lsv2_pt_...`
5. Save and redeploy

---

## 📋 Why These Are Needed

### ANTHROPIC_API_KEY
```python
# Used by create_deep_agent()
agent = create_deep_agent(
    model="claude-sonnet-4-5-20250929",  # ← Uses this key
    agent_type="ITP-Princeton",
    ...
)
```

### LANGCHAIN_API_KEY
```python
# Used by cloud subagents
from copilotagent import (
    get_cute_linear_subagent,      # ← Needs API key to connect
    get_cute_finish_itp_subagent,  # ← Needs API key to connect
)

# In cloud_subagents.py:
api_key = os.getenv("LANGCHAIN_API_KEY") or os.getenv("LANGSMITH_API_KEY")
client = RemoteGraphRunnable(
    url="https://cutelineargraph-ef1ae523c24e51ef94e330929a65833b.us.langgraph.app",
    api_key=api_key,  # ← Required to make API calls
    graph_id="cuteLinearGraph",
)
```

---

## ⚠️ Common Issues

### Error: "No module named 'dotenv'"
**Fix:** Update to `copilotagent>=0.1.7` (now includes python-dotenv)

### Error: "API key environment variable is required"
**Fix:** Ensure `LANGCHAIN_API_KEY` is set in:
- Local: `.env` file
- Cloud: LangGraph Cloud dashboard

### Error: "Authentication failed" from cloud subagents
**Fix:** Check that your `LANGCHAIN_API_KEY` is valid and has access to the deployed subagents

---

## ✅ Verification

### Test Locally
```bash
cd /Users/masoud/Desktop/WORK/DeepCopilotAgent2/agents/ITP-Princeton

# Make sure .env file exists with both keys
cat .env

# Start dev server
langgraph dev

# Should start without errors
```

### Test Cloud Deployment
After setting variables in LangGraph Cloud dashboard, the deployment should succeed without `ModuleNotFoundError`.

---

## 🔗 Quick Links

- **Anthropic Console**: https://console.anthropic.com/settings/keys
- **LangSmith Settings**: https://smith.langchain.com/settings
- **LangSmith Deployments**: https://smith.langchain.com/deployments

---

**Current Status:** ✅ Package fixed (v0.1.7), requirements updated, pushed to GitHub. Ready for LangGraph Cloud redeploy!

