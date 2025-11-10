# Station & Server Middleware Setup for ITP-Princeton Agent

## Overview

The ITP-Princeton agent now supports optional Station and Server middleware from `copilotagent>=0.1.20` for coordinating tool execution with CuteAgent's StationAgent.

## Environment Variables Required

Add these to your `.env` file:

```bash
# Required for Station & Server Middleware
STATION_TOKEN=your-station-token-here

# Optional for pause/unpause features
LANGGRAPH_TOKEN=your-langgraph-token-here
```

## Use Case: Coordinating with cute-linear Subagent

The ITP-Princeton agent uses the `cute-linear` remote subagent for borrower data extraction. Station and Server middleware can coordinate this workflow:

### Example: Filter Tool with Station Middleware

```python
from langchain_core.tools import tool
from langchain.tools import ToolRuntime

@tool
def filter_borrowers_ready_for_itp(runtime: ToolRuntime) -> str:
    """Filter borrowers ready for ITP processing."""
    # Your filtering logic here
    files = runtime.state.get("files", {})
    csv_data = files.get("/borrower_table.csv")
    
    # Process and filter borrowers
    ready_borrowers = [...]  # Your logic
    
    return {
        "ready_borrowers": ready_borrowers,
        "count": len(ready_borrowers),
        "status": "filtered"
    }

# Configure Station Middleware to sync results
filter_borrowers_ready_for_itp.metadata = {
    "station_middleware": {
        "variables": ["ready_borrowers", "count"],
        "station_id": "itp-princeton-station-1"
    }
}
```

### Example: Human Review Tool with Server Middleware

```python
@tool
def send_for_human_review(borrower_list: str) -> dict:
    """Send borrower list for human review via HITL."""
    # This tool needs exclusive access to HITL service
    human_agent = HumanAgent(...)
    result = human_agent.task(...)
    
    return {
        "review_id": result["id"],
        "status": "sent",
        "borrowers_count": len(borrower_list)
    }

# Configure Server Middleware to coordinate HITL access
send_for_human_review.metadata = {
    "server_middleware": {
        "server_id": "HITLService",
        "checkpoint": "ReviewQueue",
        "server_task_type": "ITPReview"
    }
}
```

## Using with cute-linear Subagent

The cute-linear subagent already uses StationAgent for coordination. Your ITP agent can sync with it:

```python
from copilotagent import create_deep_agent, create_remote_subagent
from copilotagent.middleware import StationMiddleware, ServerMiddleware

# Create cute-linear subagent
cute_linear_agent = create_remote_subagent(
    name="cute-linear",
    description="Extracts borrower names from screenshots...",
    url="https://cutelineargraph-xxx.us.langgraph.app",
    assistant_id="cuteLinearGraph",
    api_key=os.getenv("LANGGRAPH_API_KEY"),
)

# Create ITP agent with middleware
agent = create_deep_agent(
    model="anthropic:claude-3-5-sonnet-20241022",
    middleware=[
        ServerMiddleware(),   # Coordinates server access
        StationMiddleware(),  # Syncs with cute-linear outputs
    ],
    tools=[filter_borrowers_ready_for_itp, send_for_human_review],
    subagents=[cute_linear_agent],
    system_prompt="You are an ITP processing agent..."
)
```

## Agent State Requirements

For Server Middleware to work, include `station_thread_id` in state:

```python
# When invoking the agent
result = agent.invoke(
    {"messages": [HumanMessage(content="Process ITP documents")]},
    config={
        "configurable": {
            "thread_id": "itp-thread-123",
            "station_thread_id": "itp-princeton-station-1"  # Required for Server Middleware
        }
    }
)
```

## Workflow Example

```
1. User: "Process ITP documents for today"
   ↓
2. Agent calls cute-linear subagent (with Station coordination)
   ↓
3. cute-linear extracts borrower names → syncs to SharedState
   ↓
4. Agent uses filter_borrowers_ready_for_itp tool
   - Station Middleware syncs results after execution
   ↓
5. Agent uses send_for_human_review tool
   - Server Middleware coordinates HITL access before/after
   ↓
6. Results available in SharedState for other agents/workflows
```

## Error Handling

- **Missing `STATION_TOKEN`**: Tool returns error asking agent to report to human
- **cute-linear busy**: Server Middleware retries every 30 seconds (10min max)
- **Variable not in output**: Skipped with warning (tool still succeeds)
- **Server error**: Immediate failure with actionable error message

## Testing

1. **Verify environment**:
```bash
cd /Users/masoud/Desktop/WORK/DeepCopilotAgent2/agents/ITP-Princeton
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('STATION_TOKEN:', 'SET ✅' if os.getenv('STATION_TOKEN') else 'NOT SET ❌')
print('LANGGRAPH_TOKEN:', 'SET ✅' if os.getenv('LANGGRAPH_TOKEN') else 'NOT SET ❌')
"
```

2. **Test middleware**:
```bash
python3 -c "from copilotagent.middleware import StationMiddleware, ServerMiddleware; print('✅ Middleware available')"
```

3. **Test StationAgent**:
```bash
python3 -c "from cuteagent import StationAgent; print('✅ StationAgent available')"
```

## Documentation References

- Main Middleware Guide: `/baseCopilotAgent/MIDDLEWARE_USAGE_GUIDE.md`
- Architecture Notes: `/baseCopilotAgent/MIDDLEWARE_ARCHITECTURE_NOTES.md`
- Environment Setup: `/baseCopilotAgent/ENV_VARIABLES_SETUP.md`
- cute-linear Example: `/Users/masoud/Desktop/WORK/cutegraph/cuteLinear/src/agent/graph.py`

## Current Status

- ✅ `copilotagent>=0.1.20` with middleware support
- ✅ `cuteagent>=0.2.24` already included
- ✅ Compatible with existing cute-linear integration
- ⚠️ Middleware are **optional** - tools work without them
- ⚠️ Configure `.env` file with `STATION_TOKEN` to enable

