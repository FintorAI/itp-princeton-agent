# Environment Variables Reference - ITP-Princeton Agent

## Required Variables

```bash
# API Keys (REQUIRED)
ANTHROPIC_API_KEY=sk-ant-api03-your-key
LANGCHAIN_API_KEY=lsv2_pt_your-key

# Middleware (REQUIRED)
STATION_TOKEN=your-station-token
```

## Development Mode

```bash
# Use local copilotagent for testing unreleased features
USE_LOCAL_COPILOTAGENT=true

# Use PyPI copilotagent for production (default)
# USE_LOCAL_COPILOTAGENT=false  # or just omit
```

## Optional Variables

```bash
# Advanced middleware features
LANGGRAPH_TOKEN=your-lg-token

# Human-in-the-loop error reporting
HITL_TOKEN=your-hitl-token

# AWS document processing
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION=us-east-1
```

## ❌ Variables NOT Needed

```bash
# Don't add these - they're not used!
# STATION_THREAD_ID  ← Station ID comes from parent thread_id automatically
```

## Quick Reference

| Variable | Required | Purpose | Default |
|----------|----------|---------|---------|
| `ANTHROPIC_API_KEY` | **YES** | Claude LLM | - |
| `LANGCHAIN_API_KEY` | **YES** | LangGraph Cloud | - |
| `STATION_TOKEN` | **YES** | SharedState API | - |
| `USE_LOCAL_COPILOTAGENT` | No | Dev/Prod toggle | `false` |
| `LANGGRAPH_TOKEN` | No | Pause/unpause | - |
| `HITL_TOKEN` | No | Error reporting | - |

## Example `.env` File

```bash
# Minimal production setup
ANTHROPIC_API_KEY=sk-ant-api03-xxx
LANGCHAIN_API_KEY=lsv2_pt_xxx
STATION_TOKEN=your-token

# Development setup (add this)
USE_LOCAL_COPILOTAGENT=true
```

## How to Switch Versions

### Development Mode (Local)

```bash
# Edit .env:
USE_LOCAL_COPILOTAGENT=true

# Restart agent
langgraph dev

# Shows: "🔧 DEV MODE: Using LOCAL copilotagent..."
```

### Production Mode (PyPI)

```bash
# Edit .env:
USE_LOCAL_COPILOTAGENT=false  # or comment out

# Restart agent
langgraph dev

# Shows: "✅ Using PyPI copilotagent..."
```

**No pip commands needed!** Just toggle the flag and restart. 🚀

