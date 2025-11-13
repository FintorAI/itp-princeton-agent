# How to Open LangGraph Studio

Chrome's new security policy blocks localhost access from HTTPS sites. Here are your options:

## ✅ EASIEST: Use Tunnel (Normal Chrome, No Flags)

**Recommended for daily use:**

```bash
cd /Users/masoud/Desktop/WORK/DeepCopilotAgent2/agents/ITP-Princeton
langgraph dev --tunnel
```

- ✅ Works with **normal Chrome** (no special flags!)
- ✅ The Studio link opens automatically
- ⚠️ Requires internet connection
- ⚠️ Cloudflare tunnel can be slow sometimes

The tunnel creates a public HTTPS URL, so Chrome allows it.

---

## Alternative: Use Localhost (Faster, but Needs Browser Config)

If the tunnel is slow or unreliable:

```bash
langgraph dev  # No tunnel
```

Then choose ONE browser option:

### Option A: Firefox or Safari
Just open the link - works normally!
```
https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

### Option B: Chrome with Script
```bash
./open_studio.sh
```
This opens Chrome with security flags (separate profile for dev).

---

## Quick Summary

| Method | Command | Chrome Works? | Notes |
|--------|---------|---------------|-------|
| **Tunnel** | `langgraph dev --tunnel` | ✅ Yes, normal | Easiest! |
| **Localhost + Script** | `langgraph dev` + `./open_studio.sh` | ✅ Yes, with flags | Fastest |
| **Localhost + Firefox** | `langgraph dev` + open link | ✅ Yes, normal | Simple |

**For daily work:** Use `langgraph dev --tunnel` and just use your normal Chrome browser.

