#!/usr/bin/env bash
# Installer claude-emacs lokalt og registrer den i Claude Desktop.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
VENV="$SCRIPT_DIR/.venv"

echo "==> Oppretter virtuelt Python-miljø..."
python3 -m venv "$VENV"
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet -e "$SCRIPT_DIR"
echo "    OK: claude-emacs installert i $VENV"

echo "==> Registrerer plugin i Claude Desktop..."
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
    "command": "$VENV/bin/claude-emacs"
}

with open(config_path, "w") as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(f"    OK: {config_path} oppdatert")
PYEOF

echo ""
echo "✅ Ferdig! Neste steg:"
echo "   1. Start Emacs-server:  M-x server-start"
echo "      (eller legg til dette i init.el:)"
echo "        (require 'server)"
echo "        (unless (server-running-p) (server-start))"
echo "   2. Start Claude Desktop på nytt"
