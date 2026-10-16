#!/usr/bin/env bash
# Install Emacs MCP Bridge locally and register it with Claude Desktop.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
VENV="$SCRIPT_DIR/.venv"

echo "==> Creating a Python virtual environment..."
python3 -m venv "$VENV"
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet -e "$SCRIPT_DIR"
echo "    OK: Emacs MCP Bridge installed in $VENV"

echo "==> Registering the MCP server with Claude Desktop..."
mkdir -p "$(dirname "$CLAUDE_CONFIG")"

python3 - <<PYEOF
import json

config_path = "$CLAUDE_CONFIG"
try:
    with open(config_path) as f:
        cfg = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    cfg = {}

cfg.setdefault("mcpServers", {})
cfg["mcpServers"]["emacs"] = {
    "command": "$VENV/bin/emacs-mcp-bridge"
}

with open(config_path, "w") as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(f"    OK: {config_path} updated")
PYEOF

echo ""
echo "✅ Done! Next steps:"
echo "   1. Start the Emacs server:  M-x server-start"
echo "      (or add this to init.el:)"
echo "        (require 'server)"
echo "        (unless (server-running-p) (server-start))"
echo "   2. Restart Claude Desktop"


# Local Variables:
# mode: sh
# sh-basic-offset: 2
# End:
