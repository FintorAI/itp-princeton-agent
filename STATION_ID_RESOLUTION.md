# Station ID Resolution for Subagents

## How Station ID is Determined

SubAgentMiddleware resolves `station_id` for Station syncing using this **priority order**:

### Priority 1: Explicit in middleware_config (Highest)

```python
cute_linear = create_remote_subagent(
    name="cute-linear",
    middleware_config={
        "station": {
            "variables": ["borrower_names", "reason_code"],
            "station_id": "princeton-prod-station"  # ← Explicit station ID
        }
    }
)
```

### Priority 2: From Agent State

```python
# When invoking the agent
agent.invoke({
    "messages": [HumanMessage(content="Process ITP")],
    "station_thread_id": "my-custom-station"  # ← Passed in state
})
```

SubAgentMiddleware will find this in `runtime.state["station_thread_id"]`

### Priority 3: From Parent Thread ID (Automatic Fallback)

```python
# No explicit station_id in config or state
# SubAgentMiddleware automatically uses parent agent's thread_id

agent.invoke(
    {"messages": [...]},
    config={"configurable": {"thread_id": "itp-session-abc123"}}
)

# station_id will be: "itp-session-abc123"
```

---

## Current ITP-Princeton Configuration

```python
# In itp_agent.py

cute_linear = create_remote_subagent(
    middleware_config={
        "station": {
            "variables": ["borrower_names", "reason_code"],
            # No station_id here - will resolve at runtime!
        },
        "server": {
            "server_id": "princetonProd",  # This is for server coordination
        }
    }
)
```

## What Happens at Runtime

### Default Behavior (No Explicit Station)

```
ITP-Princeton starts with thread_id="d7f9f010-729e-466d-ae1c-67cf9eac1a0a"
    ↓
Calls task(subagent_type="cute-linear", ...)
    ↓
SubAgentMiddleware checks for station_id:
  1. Config? No
  2. State? No
  3. Parent thread_id? Yes: "d7f9f010-729e-466d-ae1c-67cf9eac1a0a"
    ↓
Uses station_id = "d7f9f010-729e-466d-ae1c-67cf9eac1a0a"
    ↓
Syncs borrower_names and reason_code to this station
```

### With Explicit Station in State

```python
# Invoke with explicit station_thread_id
agent.invoke({
    "messages": [HumanMessage(content="Process ITP")],
    "station_thread_id": "princeton-production-v2"  # ← Your custom station
})

# SubAgentMiddleware will use: "princeton-production-v2"
```

### With Explicit Station in Config

```python
# Modify itp_agent.py
cute_linear = create_remote_subagent(
    middleware_config={
        "station": {
            "variables": ["borrower_names", "reason_code"],
            "station_id": "princeton-shared-station"  # ← Explicit
        }
    }
)

# SubAgentMiddleware will ALWAYS use: "princeton-shared-station"
```

---

## Use Cases

### Use Case 1: Per-Session Isolation (Default)

```python
# No configuration needed - uses parent's thread_id
# Each session automatically gets its own station
```

**Result**: Session A and Session B have separate stations

### Use Case 2: Shared Station Across Sessions

```python
# In itp_agent.py
middleware_config={
    "station": {
        "station_id": "princeton-shared-data",  # All sessions share this
        "variables": ["borrower_names", "reason_code"]
    }
}
```

**Result**: All sessions write to same "princeton-shared-data" station

### Use Case 3: Dynamic Station Per Client

```python
# At invocation time
client_station = f"princeton-client-{client_id}"

agent.invoke({
    "messages": [...],
    "station_thread_id": client_station  # Set in state
})
```

**Result**: Each client gets their own station

---

## Summary

### For ITP-Princeton (Current Setup)

**Server Coordination:**
- Station: `"princetonProd"` (explicit, shared across all agents)
- Updates: `server[0]`, `serverThread[0]`, etc.

**Data Syncing:**
- Station: Parent's thread_id (automatic, per-session)
- Updates: `borrower_names`, `reason_code`

### How to Override

**Option A: Set in agent state**
```python
agent.invoke({
    "messages": [...],
    "station_thread_id": "my-station"
})
```

**Option B: Hardcode in middleware_config**
```python
middleware_config={
    "station": {
        "variables": [...],
        "station_id": "my-station"
    }
}
```

---

**Current Behavior**: Uses parent's thread_id (per-session isolation) ✅  
**Flexible**: Can override via state or config ✅  
**General**: Works for any use case ✅

