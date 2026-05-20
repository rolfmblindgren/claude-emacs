"""
claude-emacs — MCP-server som integrerer Claude Desktop med GNU Emacs (Mac).

Krever:
  - Emacs kjørende som server:  M-x server-start  (eller Emacs med --daemon)
  - emacsclient tilgjengelig i PATH
  - Python-pakke: mcp  (pip install mcp)
"""

import subprocess
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("emacs")


# ── Hjelpefunksjoner ──────────────────────────────────────────────────────────

def emacsclient(*args: str) -> str:
    """Kjør emacsclient med gitte argumenter og returner stdout."""
    cmd = ["emacsclient"] + list(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            err = result.stderr.strip() or result.stdout.strip()
            raise RuntimeError(f"emacsclient feilet: {err}")
        return result.stdout.strip()
    except FileNotFoundError:
        raise RuntimeError(
            "emacsclient ble ikke funnet. Legg Emacs i PATH, f.eks.:\n"
            "  export PATH=/Applications/Emacs.app/Contents/MacOS/bin:$PATH"
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("emacsclient tidsavbrudd (10 s) — er Emacs server startet?")


def elisp(expr: str) -> str:
    """Evaluer ett Elisp-uttrykk og returner resultatet."""
    return emacsclient("--eval", expr)


def unquote(s: str) -> str:
    """
    Strip Lisp-streng-anførselstegn og unescape vanlige sekvenser.
    Håndterer også propertized strings på formatet #("tekst" 0 N (face ...) ...).
    """
    # Propertized string — trekk ut bare strengdelen
    if s.startswith('#("'):
        s = s[2:]  # strip #(  →  nå starter vi med "
        # Finn slutten av strengen (første ikke-escaped ")
        i = 1
        while i < len(s):
            if s[i] == "\\" :
                i += 2
                continue
            if s[i] == '"':
                s = s[: i + 1]  # behold bare "innhold"
                break
            i += 1

    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
        s = s.replace('\\"', '"').replace("\\n", "\n").replace("\\\\", "\\")
    return s


# ── Filer ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def open_file(path: str) -> str:
    """
    Åpne en fil i Emacs.

    Args:
        path: Absolutt eller relativ filsti (~ støttes).
    """
    resolved = str(Path(path).expanduser().resolve())
    emacsclient("--no-wait", resolved)
    return f"Åpnet {resolved} i Emacs."


@mcp.tool()
def open_file_at_line(path: str, line: int) -> str:
    """
    Åpne en fil i Emacs og hopp til en bestemt linje.
    Nyttig for feilmeldinger med filsti og linjenummer.

    Args:
        path: Filsti.
        line: Linjenummer (1-indeksert).
    """
    resolved = str(Path(path).expanduser().resolve())
    emacsclient("--no-wait", f"+{line}", resolved)
    return f"Åpnet {resolved} på linje {line}."


@mcp.tool()
def get_buffer_content(buffer_name: str = "") -> str:
    """
    Hent hele innholdet i en Emacs-buffer.

    Args:
        buffer_name: Navn på buffer. Tom streng = gjeldende buffer.
    """
    if buffer_name:
        expr = (
            f'(with-current-buffer "{buffer_name}" '
            f"(buffer-substring-no-properties (point-min) (point-max)))"
        )
    else:
        expr = "(buffer-substring-no-properties (point-min) (point-max))"
    return unquote(elisp(expr))


@mcp.tool()
def write_to_buffer(content: str, buffer_name: str = "") -> str:
    """
    Erstatt hele innholdet i en buffer med ny tekst.

    Args:
        content:     Teksten som skal skrives.
        buffer_name: Navn på buffer. Tom streng = gjeldende buffer.
    """
    escaped = content.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    if buffer_name:
        expr = (
            f'(with-current-buffer "{buffer_name}" '
            f'(erase-buffer) (insert "{escaped}") nil)'
        )
    else:
        expr = f'(progn (erase-buffer) (insert "{escaped}") nil)'
    elisp(expr)
    return f"Innhold skrevet til {buffer_name or 'gjeldende buffer'}."


@mcp.tool()
def save_buffer(buffer_name: str = "") -> str:
    """
    Lagre en buffer til disk (tilsvarer C-x C-s).

    Args:
        buffer_name: Navn på buffer. Tom streng = gjeldende buffer.
    """
    if buffer_name:
        expr = f'(with-current-buffer "{buffer_name}" (save-buffer) nil)'
    else:
        expr = "(save-buffer)"
    elisp(expr)
    return f"{buffer_name or 'Gjeldende buffer'} lagret."


# ── Navigasjon ────────────────────────────────────────────────────────────────

@mcp.tool()
def list_buffers() -> str:
    """
    List alle åpne buffere i Emacs.
    Returnerer en liste med (buffer-navn filsti) per buffer.
    """
    expr = (
        "(mapconcat "
        "  (lambda (b) "
        "    (format \"%s\\t%s\" "
        "      (buffer-name b) "
        "      (or (buffer-file-name b) \"<ingen fil>\"))) "
        "  (buffer-list) \"\\n\")"
    )
    return unquote(elisp(expr))


@mcp.tool()
def get_cursor_position() -> str:
    """
    Hent gjeldende markørposisjon i aktiv buffer.
    Returnerer linje, kolonne, tegn-offset og buffer-navn.
    """
    expr = (
        "(format \"Buffer: %s  Linje: %d  Kolonne: %d  Offset: %d\" "
        "  (buffer-name) "
        "  (line-number-at-pos) "
        "  (current-column) "
        "  (point))"
    )
    return unquote(elisp(expr))


@mcp.tool()
def goto_line(line: int, buffer_name: str = "") -> str:
    """
    Hopp til en bestemt linje i Emacs.

    Args:
        line:        Linjenummer (1-indeksert).
        buffer_name: Navn på buffer. Tom streng = gjeldende buffer.
    """
    if buffer_name:
        expr = f'(with-current-buffer "{buffer_name}" (goto-line {line}) nil)'
    else:
        expr = f"(goto-line {line})"
    elisp(expr)
    return f"Hoppet til linje {line} i {buffer_name or 'gjeldende buffer'}."


# ── Region / utklippstavle ────────────────────────────────────────────────────

@mcp.tool()
def get_selected_text() -> str:
    """Hent teksten som er markert (region) i gjeldende buffer."""
    expr = (
        "(if (use-region-p) "
        "    (buffer-substring-no-properties (region-beginning) (region-end)) "
        '    "")'
    )
    result = unquote(elisp(expr))
    return result or "(ingen tekst markert)"


@mcp.tool()
def insert_at_cursor(text: str) -> str:
    """
    Sett inn tekst ved gjeldende markørposisjon i aktiv buffer.

    Args:
        text: Teksten som skal settes inn.
    """
    escaped = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    elisp(f'(insert "{escaped}")')
    return "Tekst satt inn ved markøren."


@mcp.tool()
def replace_selected_text(replacement: str) -> str:
    """
    Erstatt markert tekst (region) med ny tekst.

    Args:
        replacement: Teksten som erstatter markeringen.
    """
    escaped = replacement.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    expr = (
        f'(if (use-region-p) '
        f'  (progn (delete-region (region-beginning) (region-end)) '
        f'         (insert "{escaped}") t) '
        f'  nil)'
    )
    result = elisp(expr)
    if result == "nil":
        return "Ingen tekst er markert — ingenting ble erstattet."
    return "Markert tekst erstattet."


# ── Elisp ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def eval_elisp(expression: str) -> str:
    """
    Evaluer et vilkårlig Elisp-uttrykk i Emacs og returner resultatet.

    Args:
        expression: Gyldig Elisp, f.eks. '(+ 1 2)' eller '(buffer-name)'.
    """
    return elisp(expression)


# ── Prosjekt / søk ────────────────────────────────────────────────────────────

@mcp.tool()
def find_files(pattern: str, directory: str = ".") -> str:
    """
    Søk etter filer med et navn-mønster under en mappe.

    Args:
        pattern:   Filnavn-mønster, f.eks. '*.py' eller 'README*'.
        directory: Rotmappe for søket. Standard = gjeldende arbeidsmappe.
    """
    resolved = str(Path(directory).expanduser().resolve())
    result = subprocess.run(
        ["find", resolved, "-name", pattern, "-type", "f"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    files = result.stdout.strip()
    return files or f"Ingen filer matchet '{pattern}' under {resolved}."


# ── Start ─────────────────────────────────────────────────────────────────────

def main() -> None:
    """Entry point for uvx / pipx."""
    mcp.run()


if __name__ == "__main__":
    main()
