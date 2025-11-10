# Development Setup - ITP-Princeton Agent

## Switching Between Local and PyPI copilotagent

### Using Local Development Version (Current)

For testing unreleased features (like middleware_config for remote subagents):

```bash
cd /Users/masoud/Desktop/WORK/DeepCopilotAgent2/baseCopilotAgent

# Install in editable mode
pip uninstall copilotagent -y
pip install -e .

# Verify local version is active
python3 -c "
import copilotagent
print(f'Location: {copilotagent.__file__}')
# Should show: .../baseCopilotAgent/src/copilotagent/__init__.py
"
```

### Using PyPI Published Version

For production or when testing released features:

```bash
cd /Users/masoud/Desktop/WORK/DeepCopilotAgent2/agents/ITP-Princeton

# Uninstall local version
pip uninstall copilotagent -y

# Install from PyPI
pip install copilotagent==0.1.14

# Or install from requirements.txt
pip install -r requirements.txt

# Verify PyPI version is active
python3 -c "
import copilotagent
print(f'Location: {copilotagent.__file__}')
# Should show: .../site-packages/copilotagent/__init__.py
"
```

## Quick Switch Commands

### Switch to Local (for development)

```bash
# One-liner to switch to local editable
cd /Users/masoud/Desktop/WORK/DeepCopilotAgent2 && \
source venv/bin/activate && \
pip uninstall copilotagent -y && \
pip install -e baseCopilotAgent && \
echo "✅ Switched to LOCAL copilotagent"
```

### Switch to PyPI (for production)

```bash
# One-liner to switch to PyPI
cd /Users/masoud/Desktop/WORK/DeepCopilotAgent2 && \
source venv/bin/activate && \
pip uninstall copilotagent -y && \
pip install copilotagent==0.1.14 && \
echo "✅ Switched to PyPI copilotagent"
```

## Development Workflow Tag

Add this comment block at the top of `itp_agent.py` to document the setup:

```python
# ==============================================================================
# DEVELOPMENT MODE CONFIGURATION
# ==============================================================================
# This agent can use either:
# - LOCAL copilotagent (for testing unreleased features)
# - PyPI copilotagent (for production)
#
# TO USE LOCAL VERSION (testing middleware_config, etc.):
#   cd /Users/masoud/Desktop/WORK/DeepCopilotAgent2/baseCopilotAgent
#   pip uninstall copilotagent -y && pip install -e .
#
# TO USE PYPI VERSION (production):
#   pip uninstall copilotagent -y && pip install copilotagent==0.1.14
#
# VERIFY WHICH VERSION IS ACTIVE:
#   python3 -c "import copilotagent; print(copilotagent.__file__)"
#   - Local: .../baseCopilotAgent/src/copilotagent/__init__.py
#   - PyPI: .../site-packages/copilotagent/__init__.py
# ==============================================================================
```

## Current Status Check

Run this to see which version you're using:

```bash
python3 << 'EOF'
import copilotagent
from copilotagent import create_remote_subagent
import inspect

print("=" * 60)
print("COPILOTAGENT VERSION CHECK")
print("=" * 60)

# Check version
print(f"Version: {copilotagent.__version__}")

# Check location
location = copilotagent.__file__
if "baseCopilotAgent" in location:
    print(f"Source: LOCAL (editable)")
    print(f"Location: {location}")
else:
    print(f"Source: PyPI (installed)")
    print(f"Location: {location}")

# Check for middleware_config parameter
sig = inspect.signature(create_remote_subagent)
params = list(sig.parameters.keys())

if 'middleware_config' in params:
    print("✅ middleware_config parameter: AVAILABLE")
    print("   (Local version with unreleased features)")
else:
    print("❌ middleware_config parameter: NOT AVAILABLE")
    print("   (PyPI version 0.1.14)")

print("=" * 60)
EOF
```

Expected Output with Local Version:
```
============================================================
COPILOTAGENT VERSION CHECK
============================================================
Version: 0.1.14
Source: LOCAL (editable)
Location: /Users/masoud/Desktop/WORK/DeepCopilotAgent2/baseCopilotAgent/src/copilotagent/__init__.py
✅ middleware_config parameter: AVAILABLE
   (Local version with unreleased features)
============================================================
```

## Testing Unreleased Features

### Test middleware_config Parameter

```bash
cd /Users/masoud/Desktop/WORK/DeepCopilotAgent2/agents/ITP-Princeton

python3 -c "
from itp_agent import cute_linear, cute_finish_itp

# Check if subagents have middleware_config in their runnable
print('cute-linear runnable:', cute_linear['runnable'])
print('Has middleware_config:', hasattr(cute_linear['runnable'], 'middleware_config'))

if hasattr(cute_linear['runnable'], 'middleware_config'):
    print('Config:', cute_linear['runnable'].middleware_config)
    print('✅ Middleware config properly set')
"
```

### Test Config Injection

```python
import logging
logging.basicConfig(level=logging.INFO)

from itp_agent import agent
from langchain_core.messages import HumanMessage

# Run and check logs for config injection
result = agent.invoke(
    {"messages": [HumanMessage(content="Test")]},
    config={"configurable": {"thread_id": "test-thread"}}
)

# Look for in logs:
# "Middleware config provided for 'cute-linear': {...}"
# "Injected station_id into remote graph input: princeton-prod-station"
```

## When to Use Each Version

### Use LOCAL Version When:
- ✅ Testing new middleware features
- ✅ Developing new capabilities
- ✅ Debugging issues in copilotagent
- ✅ Making changes to baseCopilotAgent code
- ✅ **Testing middleware_config for remote subagents** ← Current task

### Use PyPI Version When:
- ✅ Running in production
- ✅ Deploying to LangGraph Cloud
- ✅ Sharing with other developers
- ✅ Version stability is important

## Environment Variables for Development

Create `agents/ITP-Princeton/.env`:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-api03-your-key
LANGCHAIN_API_KEY=lsv2_pt_your-key
STATION_TOKEN=your-station-token

# Station ID for subagents (configurable)
STATION_THREAD_ID=princeton-dev-station  # Use 'dev' for development

# Optional
LANGGRAPH_TOKEN=your-lg-token
HITL_TOKEN=your-hitl-token
```

## Before Releasing Next Version

When middleware_config changes are ready for release:

1. Test thoroughly with local version
2. Update CHANGELOG.md with new features
3. Run prepare_release.sh and release.sh
4. After PyPI deployment, switch all agents to PyPI version
5. Update documentation with new version number

## Quick Reference

| Task | Command |
|------|---------|
| Switch to Local | `pip uninstall copilotagent -y && pip install -e baseCopilotAgent` |
| Switch to PyPI | `pip uninstall copilotagent -y && pip install copilotagent==0.1.14` |
| Check Version | `python3 -c "import copilotagent; print(copilotagent.__file__)"` |
| Test Features | `python3 -c "from copilotagent import create_remote_subagent; import inspect; print(list(inspect.signature(create_remote_subagent).parameters))"` |

---

**Current Status**: ✅ Using LOCAL editable version  
**middleware_config**: ✅ Available  
**Ready for Testing**: ✅ Yes

