#!/usr/bin/env python3
"""
Stops shell commands that destroy data or rewrite shared history.

PreToolUse hook for Bash. Exit code 2 blocks the command and tells
Claude why, so it asks the user instead of retrying. Only the first
line is checked, so a heredoc or a commit message that mentions one of
these words does not trip it.
"""

import json
import re
import sys

BLOCKING_EXIT_CODE = 2

# A commit message is free text. "fix: drop table handling" is not SQL.
FREE_TEXT_COMMANDS = re.compile(r"^\s*git\s+commit\b")

BLOCKED_PATTERNS = {
    r"\bdropdb\b|\bdrop\s+(database|table|schema)\b": "drops a database object",
    r"\brm\s+-[a-z]*r[a-z]*f?\s+(/|~|\$HOME)(\s|$)": "deletes a root or home directory",
    r"\bmigrate\b.*--fake": "fakes a migration",
    r"\bflush\b.*--no-input|\bflush\b.*--noinput": "empties the database without asking",
    r"\bgit\s+push\b.*(--force\b|-f\b)": "force-pushes",
    r"\bgit\s+reset\s+--hard\b": "throws away uncommitted work",
    r"\bgit\s+clean\s+-[a-z]*f": "deletes untracked files",
}


def main() -> int:
    tool_call = json.load(sys.stdin)
    command = tool_call.get("tool_input", {}).get("command", "")
    first_line = command.strip().splitlines()[0] if command.strip() else ""
    if FREE_TEXT_COMMANDS.match(first_line):
        return 0

    for pattern, reason in BLOCKED_PATTERNS.items():
        if re.search(pattern, first_line, flags=re.IGNORECASE):
            print(
                f"BLOCKED: this command {reason}. Ask the user for explicit "
                f"permission and let them run it.",
                file=sys.stderr,
            )
            return BLOCKING_EXIT_CODE

    return 0


if __name__ == "__main__":
    sys.exit(main())
