#!/usr/bin/env bash
# Install the MCP server locally and register it with Codex.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv"

for program in python3 emacsclient codex; do
  if ! command -v "$program" >/dev/null 2>&1; then
    printf '%s is missing from PATH.\n' "$program" >&2
    exit 1
  fi
done

if codex mcp get emacs >/dev/null 2>&1; then
  printf 'Codex already has an MCP server named emacs. Check it before changing your setup.\n' >&2
  exit 1
fi

python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install -e "$SCRIPT_DIR"
codex mcp add emacs -- "$VENV/bin/emacs-mcp-bridge"

printf '\nDone. Restart Codex, then check that the Emacs server is running with:\n'
printf '  emacsclient --eval t\n'


# Local Variables:
# mode: sh
# sh-basic-offset: 2
# End:
