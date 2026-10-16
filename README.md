# Emacs MCP Bridge

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-server-blueviolet)](https://modelcontextprotocol.io)
[![Emacs](https://img.shields.io/badge/GNU%20Emacs-29%2B-7F5AB6?logo=gnuemacs&logoColor=white)](https://www.gnu.org/software/emacs/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

En lokal MCP-server som lar Codex eller Claude Desktop arbeide med GNU Emacs gjennom emacsclient. MCP-klienten starter Python-programmet ved behov. Det kjører ikke som en nettverkstjeneste på Grendel.

Dette er en annen forbindelse enn claude-code-ide.el: Den Emacs-pakken lar Claude Code i Emacs bruke en MCP-server startet av Emacs. Her går forbindelsen motsatt vei, fra en ekstern MCP-klient til Emacs.

## Før du begynner

- Python 3.10 eller nyere, Git og emacsclient.
- Emacs må kjøre som server på **samme maskin** som MCP-programmet. Sjekk med emacsclient --eval t; svaret skal være t.
- Start serveren fra Emacs med M-x server-start, eller legg dette i Emacs-oppsettet:

  ~~~elisp
  (require 'server)
  (unless (server-running-p)
    (server-start))
  ~~~

emacsclient følger normalt Emacs-pakken på Fedora. På Mac må Emacs.app sin bin-mappe eventuelt legges i PATH for programmet som starter MCP-serveren.

## Codex på Fedora

Klon repoet til et sted du vil beholde det, og kjør installasjonsprogrammet:

~~~sh
git clone https://github.com/rolfmblindgren/emacs-mcp-bridge.git ~/src/emacs-mcp-bridge
cd ~/src/emacs-mcp-bridge
./install-codex.sh
~~~

Skriptet lager .venv, installerer Python-pakken og registrerer en lokal stdio-server med navnet emacs i Codex. Det stanser dersom navnet allerede finnes, slik at et eksisterende oppsett ikke overskrives. Start Codex på nytt etterpå.

Vil du registrere den selv, kan du opprette Python-miljøet og bruke en absolutt sti:

~~~sh
python3 -m venv .venv
.venv/bin/python -m pip install -e .
codex mcp add emacs -- "$PWD/.venv/bin/emacs-mcp-bridge"
~~~

Programmet kan også legges inn som en stdio-server i ~/.codex/config.toml:

~~~toml
[mcp_servers.emacs]
command = "/absolutt/sti/til/emacs-mcp-bridge/.venv/bin/emacs-mcp-bridge"
~~~

Denne Codex-konfigurasjonen brukes av Codex på samme maskin. Den gir ikke Codex tilgang til Emacs på en annen maskin over SSH.

## Claude Desktop på Mac

Har du uv, kan du legge dette i ~/Library/Application Support/Claude/claude_desktop_config.json:

~~~json
{
  "mcpServers": {
    "emacs": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/rolfmblindgren/emacs-mcp-bridge", "emacs-mcp-bridge"]
    }
  }
}
~~~

Alternativt: klon repoet og kjør ./install.sh. Det eksisterende skriptet oppretter et Python-miljø og registrerer serveren i Claude Desktop. Start Claude Desktop på nytt etterpå.

## Tilgjengelige MCP-verktøy

| Verktøy | Hva det gjør |
|---|---|
| open_file, open_file_at_line | Åpner fil i Emacs, eventuelt på en bestemt linje |
| get_buffer_content, list_buffers | Leser buffere |
| get_cursor_position, goto_line | Leser eller endrer markørposisjon |
| get_selected_text | Leser markert tekst |
| insert_at_cursor, replace_selected_text, write_to_buffer | Endrer buffertekst |
| save_buffer | Lagrer en buffer |
| find_files | Søker etter filnavn |
| eval_elisp | Evaluerer vilkårlig Elisp; av som standard |

eval_elisp kan utføre alle operasjoner Emacs-brukeren har tilgang til. Den registreres bare når miljøvariabelen EMACS_MCP_BRIDGE_ENABLE_EVAL_ELISP=1 er satt for MCP-prosessen. Det gamle navnet CLAUDE_EMACS_ENABLE_EVAL_ELISP støttes fortsatt. I Codex kan verktøyet aktiveres ved å registrere serveren med denne kommandoen etter at en eventuell gammel emacs-oppføring er fjernet:

~~~sh
codex mcp add --env EMACS_MCP_BRIDGE_ENABLE_EVAL_ELISP=1 emacs -- /absolutt/sti/til/emacs-mcp-bridge/.venv/bin/emacs-mcp-bridge
~~~

De andre skriveverktøyene kan også endre åpne filer. Kontroller agentens foreslåtte endringer før du lagrer.

## Agentferdigheter

En SKILL.md kan beskrive hvordan en agent bør bruke MCP-verktøyene, men installerer ikke serveren. Brukeren må først ha Emacs-serveren og MCP-programmet på sin egen maskin. Denne Python-serveren er åpen kildekode under MIT-lisensen.

## Lisens

MIT. Se [LICENSE](LICENSE).

## Coda

From prompt to page, a thought can find its place.  
The cursor moves with patient, measured grace.  
Through open buffers, words return to view.  
And Emacs keeps the work both clear and true.  

