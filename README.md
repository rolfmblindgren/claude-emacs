# Emacs MCP Bridge

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-server-blueviolet)](https://modelcontextprotocol.io)
[![Emacs](https://img.shields.io/badge/GNU%20Emacs-29%2B-7F5AB6?logo=gnuemacs&logoColor=white)](https://www.gnu.org/software/emacs/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Emacs MCP Bridge lets Codex and Claude Desktop work with a running GNU Emacs through `emacsclient`. It is a local MCP server: your client starts the Python program over standard input and output. There is no server URL to enter.

This is separate from `claude-code-ide.el`. That Emacs package exposes a server to Claude Code running inside Emacs. Emacs MCP Bridge lets an MCP client outside Emacs work with your buffers.

## Before you start

- Install Python 3.10 or newer and `emacsclient`. Git is needed if you clone the repository; you can also use GitHub's **Code → Download ZIP**.
- Run Emacs as a server on **the same computer** as the bridge. Check with `emacsclient --eval t`; it should print `t`.
- To start the Emacs server, run `M-x server-start` in Emacs, or add this to your Emacs configuration:

  ~~~elisp
  (require 'server)
  (unless (server-running-p)
    (server-start))
  ~~~

On Fedora, `emacsclient` normally comes with Emacs. On macOS, you may need to add the Emacs.app `bin` directory to the path seen by your MCP client.

## Codex on Fedora

Clone the repository to a directory you plan to keep, then run the installer:

~~~sh
mkdir -p ~/src
git clone https://github.com/rolfmblindgren/emacs-mcp-bridge.git ~/src/emacs-mcp-bridge
cd ~/src/emacs-mcp-bridge
./install-codex.sh
~~~

If you downloaded the GitHub ZIP instead, extract it to a permanent directory and run `./install-codex.sh` there.

The installer creates `.venv`, installs the Python package, and registers a local stdio server named `emacs` in Codex. It stops if Codex already has a server with that name, so it does not replace your existing configuration. Restart Codex afterward.

To register it yourself, create a Python environment and use an absolute path:

~~~sh
python3 -m venv .venv
.venv/bin/python -m pip install -e .
codex mcp add emacs -- "$PWD/.venv/bin/emacs-mcp-bridge"
~~~

You can also put the stdio server in `~/.codex/config.toml`:

~~~toml
[mcp_servers.emacs]
command = "/absolute/path/to/emacs-mcp-bridge/.venv/bin/emacs-mcp-bridge"
~~~

This configuration connects Codex to Emacs on the same computer. It does not connect to Emacs on another host over SSH.

## Claude Desktop on macOS

If you have `uv`, add this to `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

Alternatively, clone or extract the repository and run `./install.sh`. That script creates a Python environment and writes the `emacs` entry in Claude Desktop's configuration. Check any existing `emacs` entry before running it. Restart Claude Desktop afterward.

## MCP tools

| Tool | What it does |
|---|---|
| `open_file`, `open_file_at_line` | Open a file in Emacs, optionally at a line number |
| `get_buffer_content`, `list_buffers` | Read buffers |
| `get_cursor_position`, `goto_line` | Read or change the cursor position |
| `get_selected_text` | Read selected text |
| `insert_at_cursor`, `replace_selected_text`, `write_to_buffer` | Edit buffer text |
| `save_buffer` | Save a buffer |
| `find_files` | Find files by name |
| `eval_elisp` | Run arbitrary Elisp; disabled by default |

`eval_elisp` can do anything your Emacs user can do. The bridge exposes it only when `EMACS_MCP_BRIDGE_ENABLE_EVAL_ELISP=1` is set for the MCP process. The old name, `CLAUDE_EMACS_ENABLE_EVAL_ELISP`, still works. In Codex, remove any existing `emacs` entry before registering a new one with this option:

~~~sh
codex mcp add --env EMACS_MCP_BRIDGE_ENABLE_EVAL_ELISP=1 emacs -- /absolute/path/to/emacs-mcp-bridge/.venv/bin/emacs-mcp-bridge
~~~

The other writing tools can also change open files. Review an agent's edits before saving them.

## Agent skills and licensing

An agent skill can guide an agent in using these MCP tools, but a skill does not install the bridge. The user must install Emacs MCP Bridge and run an Emacs server locally first. This Python server is free, open source software under the MIT license and works without a paid skill.

See [LICENSE](LICENSE) for the server's license.

## Coda

From prompt to page, a thought can find its place.  
The cursor moves with patient, measured grace.  
Through open buffers, words return to view.  
And Emacs keeps the work both clear and true.  

