#!/usr/bin/env bash
#
# LOD-MCP installer
#
# Installs the exact versions in uv.lock, writes run-mcp.sh (the command your
# AI app starts), checks that the server starts and lists its tools, and then
# prints what to paste into your app. Safe to run again at any time.
#
# Requires: uv (https://docs.astral.sh/uv/). uv downloads Python 3.13 if needed.

set -euo pipefail

BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
DIM='\033[2m'
NC='\033[0m'
if [ ! -t 1 ]; then BLUE=''; GREEN=''; RED=''; DIM=''; NC=''; fi

ok()   { echo -e "${GREEN}✓${NC} $*"; }
fail() { echo -e "${RED}✗${NC} $*" >&2; exit 1; }

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo -e "${BLUE}LOD-MCP installer${NC}\n"

# 1. uv
command -v uv >/dev/null 2>&1 \
    || fail "uv not found. Install it, then run this script again:
  curl -LsSf https://astral.sh/uv/install.sh | sh
  (or see https://docs.astral.sh/uv/getting-started/installation/)"
ok "Found $(uv --version)"

# 2. Dependencies, exactly as locked (also fetches Python 3.13 if it's missing)
echo -e "${DIM}Installing dependencies from uv.lock…${NC}"
uv sync --frozen --quiet || fail "uv sync failed. Run 'uv sync --frozen' to see the full error."
ok "Installed into .venv ($("$DIR/.venv/bin/python" --version))"

# 3. Launcher that AI apps start
cat > "$DIR/run-mcp.sh" <<EOF
#!/usr/bin/env bash
# Starts the LOD-MCP server over stdio. Written by install.sh.
export PYTHONUNBUFFERED=1
exec "$DIR/.venv/bin/lod-mcp" "\$@"
EOF
chmod +x "$DIR/run-mcp.sh"
ok "Created run-mcp.sh"

# 4. Start the server the way an AI app would and ask for its tools
TOOLS=$("$DIR/.venv/bin/python" - "$DIR/run-mcp.sh" <<'PY'
import asyncio, os, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main() -> None:
    params = StdioServerParameters(command=sys.argv[1])
    async with stdio_client(params, errlog=open(os.devnull, "w")) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print(len((await session.list_tools()).tools))

asyncio.run(asyncio.wait_for(main(), 30))
PY
) || fail "The server didn't start. Run ./run-mcp.sh to see the error."
ok "Server starts and offers $TOOLS tools"

# 5. Next steps
case "$(uname -s)" in
    Darwin) DESKTOP_CONFIG="~/Library/Application Support/Claude/claude_desktop_config.json" ;;
    Linux)  DESKTOP_CONFIG="~/.config/Claude/claude_desktop_config.json" ;;
    *)      DESKTOP_CONFIG="%APPDATA%\\Claude\\claude_desktop_config.json" ;;
esac

echo -e "\n${BLUE}Done. Now connect it to your AI app.${NC}\n"
echo "Claude Code:"
echo
echo "  claude mcp add lod-mcp -- \"$DIR/run-mcp.sh\""
echo
echo "Claude Desktop, in $DESKTOP_CONFIG:"
echo
cat <<EOF
  {
    "mcpServers": {
      "lod-mcp": { "command": "$DIR/run-mcp.sh" }
    }
  }
EOF
echo
echo "Then quit Claude Desktop completely and open it again."
echo "Other MCP apps: add a stdio server with the command $DIR/run-mcp.sh"
echo
echo "Try it: \"Look up Gromper in the LOD.\""
