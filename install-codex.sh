#!/usr/bin/env bash
# Installer MCP-serveren lokalt og registrer den i Codex.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv"

for program in python3 emacsclient codex; do
  if ! command -v "$program" >/dev/null 2>&1; then
    printf 'Mangler %s i PATH.\n' "$program" >&2
    exit 1
  fi
done

if codex mcp get emacs >/dev/null 2>&1; then
  printf 'Codex har allerede en MCP-server med navnet emacs. Kontroller den før du endrer oppsettet.\n' >&2
  exit 1
fi

python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install -e "$SCRIPT_DIR"
codex mcp add emacs -- "$VENV/bin/emacs-mcp-bridge"

printf '\nFerdig. Start Codex på nytt, og kontroller at Emacs-serveren kjører med:\n'
printf '  emacsclient --eval t\n'


# Local Variables:
# mode: sh
# sh-basic-offset: 2
# End:
