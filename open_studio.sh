#!/bin/bash
# LangGraph Studio Launcher for Chrome with PNA disabled
# Chrome's Private Network Access policy blocks HTTPS->localhost requests
# This script opens Chrome with security disabled for local development

STUDIO_URL="https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024"

echo "🚀 Opening LangGraph Studio in Chrome..."
echo "⚠️  Security disabled for local development"
echo ""

# Check if langgraph dev is running
if ! curl -s http://127.0.0.1:2024/ok > /dev/null 2>&1; then
    echo "❌ ERROR: LangGraph server not running!"
    echo "   Please run 'langgraph dev' first"
    exit 1
fi

echo "✅ LangGraph server is running"
echo ""

# Try to find Chrome
CHROME_PATH=""
if [ -d "/Applications/Google Chrome.app" ]; then
    CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
elif [ -d "$HOME/Applications/Google Chrome.app" ]; then
    CHROME_PATH="$HOME/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
elif [ -d "/Applications/Chromium.app" ]; then
    CHROME_PATH="/Applications/Chromium.app/Contents/MacOS/Chromium"
fi

if [ -z "$CHROME_PATH" ]; then
    echo "❌ Chrome not found in /Applications"
    echo "   Please open this URL manually:"
    echo "   $STUDIO_URL"
    echo ""
    echo "   Use Chrome with these flags:"
    echo "   --disable-web-security --user-data-dir=/tmp/chrome_dev_langgraph"
    exit 1
fi

echo "🌐 Opening: $STUDIO_URL"
echo ""

# Kill any existing dev Chrome instances to avoid conflicts
pkill -f "chrome_dev_langgraph" 2>/dev/null

# Launch Chrome directly
"$CHROME_PATH" \
  --disable-web-security \
  --user-data-dir="/tmp/chrome_dev_langgraph" \
  "$STUDIO_URL" \
  > /dev/null 2>&1 &

sleep 2

if pgrep -f "chrome_dev_langgraph" > /dev/null; then
    echo "✅ Chrome opened successfully!"
    echo ""
    echo "📝 Note: You'll see a warning banner 'unsupported command-line flag'"
    echo "   This is normal and safe for local development"
else
    echo "⚠️  Chrome might not have started. Try manually:"
    echo "   $STUDIO_URL"
fi

