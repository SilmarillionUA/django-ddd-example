#!/usr/bin/env python3
"""
Formats the file Claude just edited, so diffs never carry style noise.

PostToolUse hook for Edit and Write. Python files go through isort and
black, templates through djade. It formats one file, not the tree, so
it stays fast. A formatter that is not installed is skipped.
"""

import json
import subprocess
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
VENV_PYTHON = REPOSITORY_ROOT / ".venv" / "bin" / "python"
DJANGO_TARGET_VERSION = "5.2"


def python_executable() -> str:
    return str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable


def commands_for(path: Path) -> list[list[str]]:
    python = python_executable()

    if path.suffix == ".py" and "migrations" not in path.parts:
        return [
            [
                python,
                "-m",
                "isort",
                "--settings-path",
                str(REPOSITORY_ROOT),
                str(path),
            ],
            [python, "-m", "black", "--quiet", str(path)],
        ]

    if path.suffix == ".html":
        return [
            [
                python,
                "-m",
                "djade",
                "--target-version",
                DJANGO_TARGET_VERSION,
                str(path),
            ],
        ]

    return []


def main() -> int:
    tool_call = json.load(sys.stdin)
    file_path = tool_call.get("tool_input", {}).get("file_path", "")
    if not file_path or not Path(file_path).is_file():
        return 0

    for command in commands_for(Path(file_path)):
        # Output is dropped on purpose: a formatter that is missing or
        # fails must never stop Claude's edit.
        subprocess.run(
            command, cwd=REPOSITORY_ROOT, capture_output=True, check=False
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
