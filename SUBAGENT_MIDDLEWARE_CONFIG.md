# Subagent Middleware Configuration - ITP-Princeton Agent

## Overview

The ITP-Princeton agent now configures Station and Server middleware for its remote subagents (cute-linear and cute-finish-itp) **without modifying the remote deployments**.

## ✅ What's Configured

Both `cute-linear` and `cute-finish-itp` subagents are configured with:

### Station Middleware
- **Variables to sync**: `borrower_names`, `reason_code`
- **Station ID**: Configurable via `STATION_THREAD_ID` env var (default: `princeton-prod-station`)

### Server Middleware
- **Server ID**: `princetonProd`
- **Checkpoint**: `Chrome`
- **Server Index**: `0`

## How Station ID is Determined

The station_id can be configured in **three flexible ways** (priority order):

### Option 1: Environment Variable (Recommended)

Add to `.env` file:

```bash
# Explicit station ID for subagents
STATION_THREAD_ID=princeton-prod-station-v1

# Or use a dynamic value per environment
STATION_THREAD_ID=princeton-${ENVIRONMENT}-station  # e.g., princeton-dev-station
```

**In itp_agent.py:**
```python
middleware_config={
    "station": {
        "variables": ["borrower_names", "reason_code"],
        "station_id": os.getenv("STATION_THREAD_ID", "princeton-prod-station")
    },
    # ...
}
```

### Option 2: Hardcoded Value

```python
middleware_config={
    "station": {
        "variables": ["borrower_names", "reason_code"],
        "station_id": "princeton-specific-station-id"  # Explicit
    },
    # ...
}
```

### Option 3: Use Parent Thread ID (For Dynamic Scenarios)

```python
middleware_config={
    "station": {
        "variables": ["borrower_names", "reason_code"],
        "station_id_from_parent": True  # Auto-inject parent's thread_id
    },
    # ...
}
```

## Current Configuration

**File**: `agents/ITP-Princeton/itp_agent.py`

### cute-linear Subagent

```python
cute_linear = create_remote_subagent(
    name="cute-linear",
    url="https://cutelineargraph-ef1ae523c24e51ef94e330929a65833b.us.langgraph.app",
    graph_id="cuteLinearGraph",
    description="...",
    middleware_config={
        "station": {
            "variables": ["borrower_names", "reason_code"],
            "station_id": os.getenv("STATION_THREAD_ID", "princeton-prod-station")
        },
        "server": {
            "server_id": "princetonProd",
            "checkpoint": "Chrome",
            "server_index": 0
        }
    },
)
```

### cute-finish-itp Subagent

```python
cute_finish_itp = create_remote_subagent(
    name="cute-finish-itp",
    url="https://cutefinishitp-2d3fcf81a7e55dd09a66354c5c2b567c.us.langgraph.app",
    graph_id="cuteFinishITP",
    description="...",
    middleware_config={
        "station": {
            "variables": ["borrower_names", "reason_code"],
            "station_id": os.getenv("STATION_THREAD_ID", "princeton-prod-station")
        },
        "server": {
            "server_id": "princetonProd",
            "checkpoint": "Chrome",
            "server_index": 0
        }
    },
)
```

## Environment Variables

Add to `agents/ITP-Princeton/.env`:

```bash
# Required: LangChain/LangGraph
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
LANGCHAIN_API_KEY=lsv2_pt_your-key-here

# Required: Station & Server Middleware
STATION_TOKEN=your-station-token-here

# Optional: Custom station thread ID for subagents
# If not set, defaults to "princeton-prod-station"
STATION_THREAD_ID=princeton-prod-station

# Optional: Advanced features
LANGGRAPH_TOKEN=your-langgraph-token-here

# Optional: HITL
HITL_TOKEN=your-hitl-token-here
```

## What Gets Injected into Remote Graphs

When ITP-Princeton calls cute-linear or cute-finish-itp:

### Input Sent to Remote Graph

```json
{
  "user_input": "Extract borrower names",
  "messages": [...],
  
  "_middleware_config": {
    "station": {
      "variables": ["borrower_names", "reason_code"],
      "station_id": "princeton-prod-station"
    },
    "server": {
      "server_id": "princetonProd",
      "checkpoint": "Chrome",
      "server_index": 0
    }
  },
  
  "station_thread_id": "princeton-prod-station",
  "stationThreadId": "princeton-prod-station"
}
```

## How Remote Graphs Use This

The remote graphs (cute-linear, cute-finish-itp) need to:

1. **Read** `_middleware_config` from their input state
2. **Apply** it to their tools as metadata
3. **Include** Station and Server middleware in their agent configuration

See `/agents/REMOTE_SUBAGENT_MIDDLEWARE_GUIDE.md` for detailed remote graph implementation.

## Benefits of This Approach

✅ **Flexible Station IDs**: Configure per environment via env vars  
✅ **No Hardcoding**: Easy to change without code modification  
✅ **Multi-Environment**: Dev/staging/prod can use different stations  
✅ **Centralized Control**: All configuration in parent agent  
✅ **Backward Compatible**: Works with or without remote graph updates  

## Testing

### 1. Verify Configuration

```bash
cd /Users/masoud/Desktop/WORK/DeepCopilotAgent2/agents/ITP-Princeton

python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

station_id = os.getenv('STATION_THREAD_ID', 'princeton-prod-station')
print(f'Station ID that will be used: {station_id}')
print(f'STATION_TOKEN: {'SET ✅' if os.getenv('STATION_TOKEN') else 'NOT SET ❌'}')
"
```

### 2. Check Config Injection (with Logging)

```python
import logging
logging.basicConfig(level=logging.INFO)

from itp_agent import agent
from langchain_core.messages import HumanMessage

# Run agent and watch logs for:
# "Injected station_id into remote graph input: princeton-prod-station"
result = agent.invoke(
    {"messages": [HumanMessage(content="Extract borrower names")]},
    config={"configurable": {"thread_id": "test-123"}}
)
```

### 3. Verify in Remote Graph (After Update)

In cute-linear, add logging:
```python
async def extract_station_id(state: State, config: RunnableConfig) -> State:
    logging.info(f"Received station_thread_id: {state.station_thread_id}")
    logging.info(f"Received _middleware_config: {state._middleware_config}")
    # Should show: princeton-prod-station
```

## Configuration Examples for Different Scenarios

### Production Environment

```bash
# .env
STATION_THREAD_ID=princeton-prod-station
```

### Development Environment

```bash
# .env
STATION_THREAD_ID=princeton-dev-station
```

### Multi-Tenant Scenario

```python
# Dynamic station_id based on client
client_id = "client-abc"
middleware_config={
    "station": {
        "variables": ["borrower_names", "reason_code"],
        "station_id": f"princeton-{client_id}-station"
    },
    # ...
}
```

### Use Parent Thread (Session-Specific)

```python
middleware_config={
    "station": {
        "variables": ["borrower_names", "reason_code"],
        "station_id_from_parent": True  # Each session gets own station
    },
    # ...
}
```

## Next Steps

1. ✅ **ITP-Princeton agent updated** with flexible station_id configuration
2. ✅ **copilotagent 0.1.14 installed** with enhanced create_remote_subagent
3. ⚠️ **Configure .env** with `STATION_THREAD_ID` (or use default)
4. 🔲 **Update cute-linear graph** to read and apply middleware config
5. 🔲 **Update cute-finish-itp graph** to read and apply middleware config

---

**Status**: ✅ Parent configuration complete  
**Version**: copilotagent 0.1.14  
**Updated**: November 1, 2025

