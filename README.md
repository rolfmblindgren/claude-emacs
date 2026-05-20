# claude-emacs

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-server-blueviolet?logo=anthropic&logoColor=white)](https://modelcontextprotocol.io)
[![Emacs](https://img.shields.io/badge/GNU%20Emacs-29%2B-7F5AB6?logo=gnuemacs&logoColor=white)](https://www.gnu.org/software/emacs/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![macOS](https://img.shields.io/badge/macOS-only-lightgrey?logo=apple&logoColor=white)](https://www.apple.com/macos/)
[![Built with Claude](https://img.shields.io/badge/built%20with-Claude-orange?logo=anthropic&logoColor=white)](https://claude.ai)

MCP-server som kobler [Claude Desktop](https://claude.ai/download) til GNU Emacs på Mac via `emacsclient`.

## Installasjon

### Alternativ 1 — uvx (anbefalt, ingen installasjon)

Legg til i `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "emacs": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/rolfmblindgren/claude-emacs", "claude-emacs"]
    }
  }
}
```

`uvx` henter og kjører pakken automatisk. Krever at [uv er installert](https://docs.astral.sh/uv/getting-started/installation/):

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Alternativ 2 — pipx

```sh
pipx install git+https://github.com/rolfmblindgren/claude-emacs
```

Legg til i `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "emacs": {
      "command": "claude-emacs"
    }
  }
}
```

### Alternativ 3 — manuelt (klon + venv)

```sh
git clone https://github.com/rolfmblindgren/claude-emacs ~/src/claude-emacs
cd ~/src/claude-emacs
./install.sh
```

## Emacs-oppsett

Legg til i `init.el` for automatisk serverstart:

```elisp
(require 'server)
(unless (server-running-p)
  (server-start))
```

Sørg for at `emacsclient` er i PATH (f.eks. i `~/.zshrc`):

```sh
export PATH="/Applications/Emacs.app/Contents/MacOS/bin:$PATH"
```

Start Claude Desktop på nytt etter konfigurasjonsendringer.

## Verktøy

| Verktøy | Beskrivelse |
|---------|-------------|
| `open_file` | Åpne en fil i Emacs |
| `open_file_at_line` | Åpne fil og hopp til linje |
| `get_buffer_content` | Hent innholdet i en buffer |
| `write_to_buffer` | Skriv ny tekst til en buffer |
| `save_buffer` | Lagre buffer til disk (C-x C-s) |
| `list_buffers` | List alle åpne buffere |
| `get_cursor_position` | Hent linje/kolonne/offset |
| `goto_line` | Hopp til en linje |
| `get_selected_text` | Hent markert tekst (region) |
| `insert_at_cursor` | Sett inn tekst ved markøren |
| `replace_selected_text` | Erstatt markert tekst |
| `eval_elisp` | Evaluer et Elisp-uttrykk |
| `find_files` | Søk etter filer med navn-mønster |

## Lisens

MIT
