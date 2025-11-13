#!/bin/bash
# Start LangGraph with ngrok tunnel (more reliable than Cloudflare)

echo "🚀 Starting LangGraph with ngrok tunnel..."
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok not installed!"
    echo ""
    echo "Install with: brew install ngrok"
    echo "Or download from: https://ngrok.com/download"
    exit 1
fi

echo "✅ ngrok found"
echo ""

# Start langgraph in background
cd "$(dirname "$0")"
echo "Starting langgraph dev server..."
langgraph dev > /tmp/langgraph.log 2>&1 &
LANGGRAPH_PID=$!

# Wait for server to start
echo "Waiting for server to start..."
sleep 5

if ! curl -s http://127.0.0.1:2024/ok > /dev/null 2>&1; then
    echo "❌ Failed to start langgraph server"
    kill $LANGGRAPH_PID 2>/dev/null
    exit 1
fi

echo "✅ LangGraph server started"
echo ""

# Start ngrok tunnel
echo "Starting ngrok tunnel..."
ngrok http 2024 > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!

sleep 3

# Get ngrok URL
NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | python3 -c "import sys, json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])" 2>/dev/null)

if [ -z "$NGROK_URL" ]; then
    echo "❌ Failed to get ngrok URL"
    kill $LANGGRAPH_PID $NGROK_PID 2>/dev/null
    exit 1
fi

echo "✅ Tunnel created: $NGROK_URL"
echo ""
echo "🎨 Studio URL:"
echo "https://smith.langchain.com/studio/?baseUrl=$NGROK_URL"
echo ""
echo "Opening in browser..."
open "https://smith.langchain.com/studio/?baseUrl=$NGROK_URL"
echo ""
echo "Press Ctrl+C to stop..."

# Wait for interrupt
trap "kill $LANGGRAPH_PID $NGROK_PID 2>/dev/null; exit" INT TERM
wait

