# ITP-Princeton Agent - Quick Start Guide

## Development Mode Switching (NEW!)

The agent now supports switching between LOCAL and PyPI copilotagent using an environment variable flag!

### Method 1: Environment Variable Flag (Recommended)

**Add to `.env` file:**

```bash
# Development mode - use local copilotagent
USE_LOCAL_COPILOTAGENT=true

# Production mode - use PyPI copilotagent  
# USE_LOCAL_COPILOTAGENT=false  # or just comment out
```

**How it works:**
- `USE_LOCAL_COPILOTAGENT=true` → Uses `/baseCopilotAgent/src` (local development)
- `USE_LOCAL_COPILOTAGENT=false` or omitted → Uses installed package

**Start agent:**
```bash
cd /Users/masoud/Desktop/WORK/DeepCopilotAgent2/agents/ITP-Princeton
langgraph dev  # Automatically reads USE_LOCAL_COPILOTAGENT from .env
```

**Or test directly:**
```bash
USE_LOCAL_COPILOTAGENT=true python3 itp_agent.py
```

### Method 2: Temporary Override (Command Line)

```bash
# Test with local version once
USE_LOCAL_COPILOTAGENT=true langgraph dev

# Test with PyPI version once  
USE_LOCAL_COPILOTAGENT=false langgraph dev
```

## Environment Variables

**Required `.env` file:**

```bash
# API Keys
ANTHROPIC_API_KEY=sk-ant-api03-your-key
LANGCHAIN_API_KEY=lsv2_pt_your-key

# Middleware (required if remote graphs use middleware)
STATION_TOKEN=your-station-token

# Development mode toggle
USE_LOCAL_COPILOTAGENT=true  # or false for production

# Optional
LANGGRAPH_TOKEN=your-lg-token
HITL_TOKEN=your-hitl-token
```

## Middleware Configuration

### Station ID Resolution

The subagents use **`station_id_from_parent: True`**, which means:
- Station ID = Parent ITP-Princeton agent's thread_id
- Each session/thread gets its own isolated station
- No need for `STATION_THREAD_ID` env variable!

### Configuration Applied to Subagents

**cute-linear:**
```python
middleware_config={
    "station": {
        "variables": ["borrower_names", "reason_code"],
        "station_id_from_parent": True  # Uses parent thread_id
    },
    "server": {
        "server_id": "princetonProd",
        "checkpoint": "Chrome",
        "server_index": 0
    }
}
```

**cute-finish-itp:**
```python
middleware_config={
    "station": {
        "variables": ["borrower_names", "reason_code"],
        "station_id_from_parent": True  # Uses parent thread_id
    },
    "server": {
        "server_id": "princetonProd",
        "checkpoint": "Chrome",
        "server_index": 0
    }
}
```

## Quick Commands

### Check Which Version is Active

```bash
python3 -c "import copilotagent; print(copilotagent.__file__)"
```

- Local: `.../baseCopilotAgent/src/copilotagent/__init__.py`
- PyPI: `.../site-packages/copilotagent/__init__.py`

### Test Local Version

```bash
cd /Users/masoud/Desktop/WORK/DeepCopilotAgent2/agents/ITP-Princeton
USE_LOCAL_COPILOTAGENT=true python3 itp_agent.py
```

Should show:
```
🔧 DEV MODE: Using LOCAL copilotagent from .../baseCopilotAgent/src
✅ Using LOCAL copilotagent: .../baseCopilotAgent/src/copilotagent/__init__.py
```

### Test PyPI Version

```bash
USE_LOCAL_COPILOTAGENT=false python3 itp_agent.py
```

Should show:
```
✅ Using PyPI copilotagent: .../site-packages/copilotagent/__init__.py
```

## Testing Middleware Config

```bash
cd /Users/masoud/Desktop/WORK/DeepCopilotAgent2/agents/ITP-Princeton

USE_LOCAL_COPILOTAGENT=true python3 -c "
from itp_agent import cute_linear, cute_finish_itp

# Check configuration
print('cute-linear server:', cute_linear['runnable'].middleware_config['server']['server_id'])
print('cute-finish-itp server:', cute_finish_itp['runnable'].middleware_config['server']['server_id'])
print('✅ Both configured with princetonProd')
"
```

## Development Workflow

### 1. Make Changes to baseCopilotAgent

```bash
cd /Users/masoud/Desktop/WORK/DeepCopilotAgent2/baseCopilotAgent/src/copilotagent
# Edit files...
```

### 2. Test with ITP-Princeton Agent

```bash
cd /Users/masoud/Desktop/WORK/DeepCopilotAgent2/agents/ITP-Princeton

# Add to .env:
# USE_LOCAL_COPILOTAGENT=true

langgraph dev
# Changes in baseCopilotAgent are immediately reflected!
```

### 3. Switch to Production

```bash
# Edit .env:
# USE_LOCAL_COPILOTAGENT=false  # or comment out

langgraph dev
# Now using stable PyPI version
```

## Advantages of Flag-Based Switching

✅ **No pip install/uninstall** - Just change env var  
✅ **Instant switching** - Edit .env and restart  
✅ **Per-session control** - Use different versions simultaneously  
✅ **Simple** - Just one flag to toggle  
✅ **Safe** - No risk of breaking installed packages  

## Common Scenarios

### Scenario 1: Testing New Features

```bash
# .env
USE_LOCAL_COPILOTAGENT=true

# Test middleware_config, new tools, etc.
langgraph dev
```

### Scenario 2: Production Deployment

```bash
# .env  
# USE_LOCAL_COPILOTAGENT=false  # Commented out

# Uses stable PyPI version
langgraph dev
```

### Scenario 3: Debugging Issues

```bash
# Terminal 1: PyPI version
USE_LOCAL_COPILOTAGENT=false langgraph dev --port 2024

# Terminal 2: Local version
USE_LOCAL_COPILOTAGENT=true langgraph dev --port 2025

# Compare behavior side-by-side!
```

## Current Setup

**Currently Active:**
- 📍 Local copilotagent installed in editable mode
- ✅ middleware_config parameter available
- ✅ Station ID uses parent thread_id (no env var needed)
- ✅ Both subagents configured with princetonProd server
- ✅ Flag-based switching implemented

**To Use:**
1. Set `USE_LOCAL_COPILOTAGENT=true` in `.env`
2. Run `langgraph dev`
3. Agent automatically uses local version!

---

**Pro Tip**: Keep both the editable installation AND a comment in .env showing how to toggle:

```bash
# Development: use local copilotagent with latest unreleased features
USE_LOCAL_COPILOTAGENT=true

# Production: use stable PyPI copilotagent
# USE_LOCAL_COPILOTAGENT=false
```

This way you can quickly comment/uncomment to switch! 🚀

