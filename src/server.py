"""
Emacs MCP Bridge — a local MCP server connecting AI clients to GNU Emacs.

Requires:
  - Emacs running as a server: M-x server-start (or Emacs with --daemon)
  - emacsclient available in PATH
  - Python package: mcp (pip install mcp)
"""

import base64
import os
import subprocess
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("emacs")


# ── Helpers ───────────────────────────────────────────────────────────────────

def emacsclient(*args: str) -> str:
    """Run emacsclient with the given arguments and return stdout."""
    cmd = ["emacsclient"] + list(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            err = result.stderr.strip() or result.stdout.strip()
            raise RuntimeError(f"emacsclient failed: {err}")
        return result.stdout.strip()
    except FileNotFoundError:
        raise RuntimeError(
            "emacsclient was not found. Install Emacs and add emacsclient to PATH."
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("emacsclient timed out after 10 seconds. Is the Emacs server running?")


def elisp(expr: str) -> str:
    """Evaluate one Elisp expression and return its result."""
    return emacsclient("--eval", expr)


def elisp_string(value: str) -> str:
  """Build an Elisp expression for arbitrary UTF-8 text without code injection."""
  encoded = base64.b64encode(value.encode("utf-8")).decode("ascii")
  return f'(decode-coding-string (base64-decode-string "{encoded}") \'utf-8)'


def unquote(s: str) -> str:
    """
    Strip Lisp string quotes and unescape common sequences.
    Also handle propertized strings in the form #("text" 0 N (face ...) ...).
    """
    # Propertized string — keep only the string portion.
    if s.startswith('#("'):
        s = s[2:]  # Strip #(; the remainder now starts with ".
        # Find the end of the string (the first unescaped ").
        i = 1
        while i < len(s):
            if s[i] == "\\" :
                i += 2
                continue
            if s[i] == '"':
                s = s[: i + 1]  # Keep only "content".
                break
            i += 1

    if s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
        s = s.replace('\\"', '"').replace("\\n", "\n").replace("\\\\", "\\")
    return s


# ── Files ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def open_file(path: str) -> str:
    """
    Open a file in Emacs.

    Args:
        path: Absolute or relative file path (~ is supported).
    """
    resolved = str(Path(path).expanduser().resolve())
    emacsclient("--no-wait", resolved)
    return f"Opened {resolved} in Emacs."


@mcp.tool()
def open_file_at_line(path: str, line: int) -> str:
    """
    Open a file in Emacs and go to a specific line.
    Useful for errors that include a file path and line number.

    Args:
        path: File path.
        line: Line number (starting at 1).
    """
    resolved = str(Path(path).expanduser().resolve())
    emacsclient("--no-wait", f"+{line}", resolved)
    return f"Opened {resolved} at line {line}."


@mcp.tool()
def get_buffer_content(buffer_name: str = "") -> str:
    """
    Get the full contents of an Emacs buffer.

    Args:
        buffer_name: Buffer name. Empty string means the current buffer.
    """
    if buffer_name:
        expr = (
            f'(with-current-buffer {elisp_string(buffer_name)} '
            f"(buffer-substring-no-properties (point-min) (point-max)))"
        )
    else:
        expr = "(buffer-substring-no-properties (point-min) (point-max))"
    return unquote(elisp(expr))


@mcp.tool()
def write_to_buffer(content: str, buffer_name: str = "") -> str:
    """
    Replace the entire contents of a buffer with new text.

    Args:
        content: Text to write.
        buffer_name: Buffer name. Empty string means the current buffer.
    """
    content_expr = elisp_string(content)
    if buffer_name:
        expr = (
            f'(with-current-buffer {elisp_string(buffer_name)} '
            f'(erase-buffer) (insert {content_expr}) nil)'
        )
    else:
        expr = f'(progn (erase-buffer) (insert {content_expr}) nil)'
    elisp(expr)
    return f"Content written to {buffer_name or 'the current buffer'}."


@mcp.tool()
def save_buffer(buffer_name: str = "") -> str:
    """
    Save a buffer to disk (equivalent to C-x C-s).

    Args:
        buffer_name: Buffer name. Empty string means the current buffer.
    """
    if buffer_name:
        expr = f'(with-current-buffer {elisp_string(buffer_name)} (save-buffer) nil)'
    else:
        expr = "(save-buffer)"
    elisp(expr)
    return f"{buffer_name or 'The current buffer'} was saved."


# ── Navigation ────────────────────────────────────────────────────────────────

@mcp.tool()
def list_buffers() -> str:
    """
    List all open buffers in Emacs.
    Return one buffer name and file path per line.
    """
    expr = (
        "(mapconcat "
        "  (lambda (b) "
        "    (format \"%s\\t%s\" "
        "      (buffer-name b) "
        "      (or (buffer-file-name b) \"<no file>\"))) "
        "  (buffer-list) \"\\n\")"
    )
    return unquote(elisp(expr))


@mcp.tool()
def get_cursor_position() -> str:
    """
    Get the cursor position in the current buffer.
    Return the buffer name, line, column, and character offset.
    """
    expr = (
        "(format \"Buffer: %s  Line: %d  Column: %d  Offset: %d\" "
        "  (buffer-name) "
        "  (line-number-at-pos) "
        "  (current-column) "
        "  (point))"
    )
    return unquote(elisp(expr))


@mcp.tool()
def goto_line(line: int, buffer_name: str = "") -> str:
    """
    Go to a specific line in Emacs.

    Args:
        line: Line number (starting at 1).
        buffer_name: Buffer name. Empty string means the current buffer.
    """
    if buffer_name:
        expr = f'(with-current-buffer {elisp_string(buffer_name)} (goto-line {line}) nil)'
    else:
        expr = f"(goto-line {line})"
    elisp(expr)
    return f"Moved to line {line} in {buffer_name or 'the current buffer'}."


# ── Selection ─────────────────────────────────────────────────────────────────

@mcp.tool()
def get_selected_text() -> str:
    """Get selected text (the region) in the current buffer."""
    expr = (
        "(if (use-region-p) "
        "    (buffer-substring-no-properties (region-beginning) (region-end)) "
        '    "")'
    )
    result = unquote(elisp(expr))
    return result or "(no text selected)"


@mcp.tool()
def insert_at_cursor(text: str) -> str:
    """
    Insert text at the cursor in the current buffer.

    Args:
        text: Text to insert.
    """
    elisp(f'(insert {elisp_string(text)})')
    return "Text inserted at the cursor."


@mcp.tool()
def replace_selected_text(replacement: str) -> str:
    """
    Replace selected text (the region) with new text.

    Args:
        replacement: Text to insert in place of the selection.
    """
    expr = (
        f'(if (use-region-p) '
        f'  (progn (delete-region (region-beginning) (region-end)) '
        f'         (insert {elisp_string(replacement)}) t) '
        f'  nil)'
    )
    result = elisp(expr)
    if result == "nil":
        return "No text is selected; nothing was replaced."
    return "Selected text replaced."


# ── Elisp ─────────────────────────────────────────────────────────────────────

def eval_elisp(expression: str) -> str:
    """
    Evaluate an arbitrary Elisp expression in Emacs and return its result.

    Args:
        expression: Valid Elisp, such as '(+ 1 2)' or '(buffer-name)'.
    """
    return elisp(expression)


enable_eval_elisp = os.environ.get("EMACS_MCP_BRIDGE_ENABLE_EVAL_ELISP")
if enable_eval_elisp is None:
  enable_eval_elisp = os.environ.get("CLAUDE_EMACS_ENABLE_EVAL_ELISP", "")

if enable_eval_elisp.lower() in {"1", "true", "yes", "on"}:
  mcp.tool()(eval_elisp)


# ── Project search ────────────────────────────────────────────────────────────

@mcp.tool()
def find_files(pattern: str, directory: str = ".") -> str:
    """
    Find files matching a name pattern beneath a directory.

    Args:
        pattern: File name pattern, such as '*.py' or 'README*'.
        directory: Search root. Defaults to the current working directory.
    """
    resolved = str(Path(directory).expanduser().resolve())
    result = subprocess.run(
        ["find", resolved, "-name", pattern, "-type", "f"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    files = result.stdout.strip()
    return files or f"No files matched '{pattern}' under {resolved}."


# ── Start ─────────────────────────────────────────────────────────────────────

def main() -> None:
    """Entry point for uvx / pipx."""
    mcp.run()


if __name__ == "__main__":
    main()
