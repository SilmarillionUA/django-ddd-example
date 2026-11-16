#!/usr/bin/env python3
"""
Checks that imports in the apps root point inward only.

Rules, for files outside tests:

- domain/ may not import application/ or infrastructure/.
- application/ may not import infrastructure/.
- domain/ and application/ may not import another local app.

As a Claude Code PostToolUse hook it reads the tool call from stdin and
checks the edited file. Exit code 2 sends the report back to Claude,
which then fixes the import. The hook does nothing in a project without
.claude/django-ddd.json. With --all it checks every file, for
CI and the check-architecture command.

The apps root comes from the config file. There is no default path.

This file imports nothing from the plugin, so the init skill can
copy it into a project for CI.
"""

from __future__ import annotations

import ast
import json
import os
import sys
from pathlib import Path

PROJECT_DIR_VARIABLE = "CLAUDE_PROJECT_DIR"
CONFIG_PATH = Path(".claude") / "django-ddd.json"
APPS_ROOT_KEY = "apps_root"
CHECK_ALL_FLAG = "--all"
MISSING_APPS_ROOT_MESSAGE = (
    f'No apps root set. Add "{APPS_ROOT_KEY}" to {CONFIG_PATH}, '
    f"as a path relative to the project root."
)

DOMAIN = "domain"
APPLICATION = "application"
INFRASTRUCTURE = "infrastructure"
TESTS = "tests"

FORBIDDEN_LAYERS = {
    DOMAIN: (APPLICATION, INFRASTRUCTURE),
    APPLICATION: (INFRASTRUCTURE,),
}

BLOCKING_EXIT_CODE = 2
FAILURE_EXIT_CODE = 1


def project_root() -> Path:
    return Path(os.environ.get(PROJECT_DIR_VARIABLE) or Path.cwd()).resolve()


def load_config(*, root: Path) -> dict | None:
    config_file = root / CONFIG_PATH
    if not config_file.is_file():
        return None

    return json.loads(config_file.read_text())


def local_apps(*, apps_root: Path) -> set[str]:
    return {
        path.name for path in apps_root.iterdir() if (path / DOMAIN).is_dir()
    }


def layer_of(path: Path, *, apps_root: Path) -> tuple[str, str] | None:
    """The (app, layer) a file belongs to, or None when no rule applies."""
    try:
        parts = path.resolve().relative_to(apps_root).parts
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


def violations(
    path: Path, *, apps: set[str], apps_root: Path, root: Path
) -> list[str]:
    location = layer_of(path, apps_root=apps_root)
    if location is None:
        return []

    app_name, layer = location
    relative = path.resolve().relative_to(root)
    found = []

    for line, module in imported_modules(path.read_text()):
        parts = module.split(".")
        target_app = parts[0]
        if target_app not in apps:
            continue

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


def check_all(*, apps_root: Path, root: Path) -> int:
    if not apps_root.is_dir():
        print(f"Apps root not found: {apps_root}", file=sys.stderr)
        return FAILURE_EXIT_CODE

    apps = local_apps(apps_root=apps_root)
    found = [
        problem
        for path in sorted(apps_root.rglob("*.py"))
        for problem in violations(
            path, apps=apps, apps_root=apps_root, root=root
        )
    ]

    for problem in found:
        print(problem)

    return FAILURE_EXIT_CODE if found else 0


def check_hook_input(*, apps_root: Path, root: Path) -> int:
    if not apps_root.is_dir():
        return 0

    tool_call = json.load(sys.stdin)
    file_path = tool_call.get("tool_input", {}).get("file_path", "")
    if not file_path or not Path(file_path).is_file():
        return 0

    found = violations(
        Path(file_path),
        apps=local_apps(apps_root=apps_root),
        apps_root=apps_root,
        root=root,
    )
    if not found:
        return 0

    print("DDD layer rule broken:", file=sys.stderr)
    for problem in found:
        print(problem, file=sys.stderr)

    return BLOCKING_EXIT_CODE


def main() -> int:
    root = project_root()
    config = load_config(root=root)
    check_everything = CHECK_ALL_FLAG in sys.argv

    # The hook runs in every project that has the plugin on. Only a
    # project with the config file has asked for the check.
    if config is None and not check_everything:
        return 0

    # No path is guessed. A wrong guess would check nothing and pass.
    configured_apps_root = (config or {}).get(APPS_ROOT_KEY)
    if not configured_apps_root:
        print(MISSING_APPS_ROOT_MESSAGE, file=sys.stderr)
        return FAILURE_EXIT_CODE

    apps_root = root / configured_apps_root
    if check_everything:
        return check_all(apps_root=apps_root, root=root)

    return check_hook_input(apps_root=apps_root, root=root)


if __name__ == "__main__":
    sys.exit(main())
