#!/bin/bash
#
# LOD-MCP Installation Script
# Requires: uv (https://docs.astral.sh/uv/)
#

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${BLUE}=== LOD-MCP Installation ===${NC}\n"

# Check uv
if ! command -v uv >/dev/null 2>&1; then
    echo -e "${RED}✗ uv not found${NC} — install it: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi
echo -e "${GREEN}✓${NC} Found $(uv --version)"

# Check Python 3.13+
PYTHON_VERSION=$(uv run python --version 2>&1 | head -1 || python3 --version 2>&1)
MAJOR=$(echo "$PYTHON_VERSION" | grep -oE '[0-9]+' | head -1)
MINOR=$(echo "$PYTHON_VERSION" | grep -oE '[0-9]+' | sed -n '2p')
if [ "$MAJOR" -lt 3 ] || { [ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 13 ]; }; then
    echo -e "${RED}✗ Python 3.13+ required (found $PYTHON_VERSION)${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} $PYTHON_VERSION"

# Create venv + install
echo -e "\n${BLUE}Setting up…${NC}"
uv venv "$SCRIPT_DIR/.venv" --python 3.13
uv pip install --python "$SCRIPT_DIR/.venv/bin/python" -e "$SCRIPT_DIR"

# Create wrapper
cat > "$SCRIPT_DIR/run-mcp.sh" << EOF
#!/bin/bash
export PYTHONUNBUFFERED=1
exec "$SCRIPT_DIR/.venv/bin/lod-mcp"
EOF
chmod +x "$SCRIPT_DIR/run-mcp.sh"
echo -e "${GREEN}✓${NC} Created run-mcp.sh"

# Quick smoke test
if "$SCRIPT_DIR/.venv/bin/python" -c "from server.main import main" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Imports OK"
else
    echo -e "${RED}✗${NC} Import check failed"
    exit 1
fi

# Claude config hint
echo -e "\n${BLUE}=== Done! ===${NC}"
echo "Add to Claude Desktop config:"
echo
echo "  ~/Library/Application Support/Claude/claude_desktop_config.json"
echo
cat << EOF
{
  "mcpServers": {
    "lod-mcp": {
      "command": "$SCRIPT_DIR/run-mcp.sh"
    }
  }
}
EOF
echo
echo "Then restart Claude (Cmd+Q → reopen)."