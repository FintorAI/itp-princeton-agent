#!/bin/bash
# Start LangGraph with tunnel and open in normal Chrome
# No special flags needed - just normal Chrome!

echo "🚀 Starting LangGraph with Cloudflare tunnel..."
echo ""
echo "This will:"
echo "  1. Start LangGraph dev server"
echo "  2. Create a public tunnel URL"
echo "  3. Open it in your normal Chrome browser"
echo ""
echo "Press Ctrl+C to stop the server when done."
echo ""
echo "Starting in 3 seconds..."
sleep 3

cd "$(dirname "$0")"

# Start langgraph with tunnel
langgraph dev --tunnel

