#!/bin/bash
# Just copy the Studio URL to clipboard

STUDIO_URL="https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024"

# Check if server is running
if curl -s http://127.0.0.1:2024/ok > /dev/null 2>&1; then
    echo "✅ LangGraph server is running"
else
    echo "⚠️  LangGraph server not detected on port 2024"
    echo "   Make sure 'langgraph dev' is running"
fi

echo ""
echo "📋 Studio URL copied to clipboard:"
echo "$STUDIO_URL"
echo ""
echo "Paste into your browser."
echo ""
echo "⚠️  IMPORTANT - Use one of these browsers with proper settings:"
echo ""
echo "Option 1 - Chrome/Chromium (requires flags):"
echo "  Close all Chrome windows, then run in terminal:"
echo "  /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \\"
echo "    --disable-web-security \\"
echo "    --user-data-dir=/tmp/chrome_dev \\"
echo "    \"$STUDIO_URL\""
echo ""
echo "Option 2 - Firefox or Safari:"
echo "  Just paste the URL - no flags needed!"
echo ""

# Copy to clipboard
echo "$STUDIO_URL" | pbcopy
echo "✅ URL in clipboard - just paste it!"

