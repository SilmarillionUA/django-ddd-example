#!/usr/bin/env python3
"""
Checks that imports in src/apps point inward only.

Rules, for files outside tests:

- domain/ may not import application/ or infrastructure/.
- application/ may not import infrastructure/.
- domain/ and application/ may not import another local app.

As a Claude Code PostToolUse hook it reads the tool call from stdin and
checks the edited file. Exit code 2 sends the report back to Claude,
which then fixes the import. With --all it checks every file, for
`make lint` and CI.
"""

import ast
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
APPS_ROOT = REPOSITORY_ROOT / "src" / "apps"

DOMAIN = "domain"
APPLICATION = "application"
INFRASTRUCTURE = "infrastructure"
TESTS = "tests"

FORBIDDEN_LAYERS = {
    DOMAIN: (APPLICATION, INFRASTRUCTURE),
    APPLICATION: (INFRASTRUCTURE,),
}

BLOCKING_EXIT_CODE = 2


def local_apps() -> set[str]:
    return {
        path.name for path in APPS_ROOT.iterdir() if (path / DOMAIN).is_dir()
    }


def layer_of(path: Path) -> tuple[str, str] | None:
    """The (app, layer) a file belongs to, or None when no rule applies."""
    try:
        parts = path.resolve().relative_to(APPS_ROOT).parts
    except ValueError:
        return None

    if len(parts) < 3 or TESTS in parts or path.suffix != ".py":
        return None

    app_name, layer = parts[0], parts[1]
    if layer not in FORBIDDEN_LAYERS:
        return None

    return app_name, layer


def imported_modules(source: str) -> list[tuple[int, str]]:
    modules = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            modules.extend((node.lineno, alias.name) for alias in node.names)
        elif (
            isinstance(node, ast.ImportFrom) and node.module and not node.level
        ):
            modules.append((node.lineno, node.module))

    return modules


def violations(path: Path, *, apps: set[str]) -> list[str]:
    location = layer_of(path)
    if location is None:
        return []

    app_name, layer = location
    found = []

    for line, module in imported_modules(path.read_text()):
        parts = module.split(".")
        target_app = parts[0]
        if target_app not in apps:
            continue

        relative = path.relative_to(REPOSITORY_ROOT)
        if target_app != app_name:
            found.append(
                f"{relative}:{line}: {layer} imports another app ({module}). "
                f"Add an interface in {app_name}/domain/interfaces.py and a "
                f"gateway in {app_name}/infrastructure/gateways.py."
            )
        elif len(parts) > 1 and parts[1] in FORBIDDEN_LAYERS[layer]:
            found.append(
                f"{relative}:{line}: {layer} imports {parts[1]} ({module}). "
                f"Imports must point inward: infrastructure -> application "
                f"-> domain."
            )

    return found


def check_all() -> int:
    apps = local_apps()
    found = [
        problem
        for path in sorted(APPS_ROOT.rglob("*.py"))
        for problem in violations(path, apps=apps)
    ]

    for problem in found:
        print(problem)

    return 1 if found else 0


def check_hook_input() -> int:
    tool_call = json.load(sys.stdin)
    file_path = tool_call.get("tool_input", {}).get("file_path", "")
    if not file_path or not Path(file_path).is_file():
        return 0

    found = violations(Path(file_path), apps=local_apps())
    if not found:
        return 0

    print("DDD layer rule broken:", file=sys.stderr)
    for problem in found:
        print(problem, file=sys.stderr)

    return BLOCKING_EXIT_CODE


if __name__ == "__main__":
    sys.exit(check_all() if "--all" in sys.argv else check_hook_input())
