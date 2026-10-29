---
name: new-app
description: Scaffold a new bounded context as a Django app with domain, application and infrastructure layers, and wire it into settings. Use when the user asks for a new app or a new bounded context.
---

# Create a new Django app with DDD layers

Create a new app with the name the user gives under `src/apps/`, following `catalog` and `lending`.

## Directory structure

```
src/apps/{app_name}/
├── __init__.py
├── CLAUDE.md
├── conftest.py
├── domain/
│   ├── __init__.py
│   ├── models.py
│   ├── managers.py
│   ├── choices.py
│   ├── exceptions.py
│   ├── interfaces.py
│   ├── settings.py
│   ├── types.py
│   ├── services/__init__.py
│   └── tests/__init__.py
├── application/
│   ├── __init__.py
│   ├── use_cases/__init__.py
│   └── tests/__init__.py
└── infrastructure/
    ├── __init__.py
    ├── apps.py
    ├── admin.py
    ├── di.py
    ├── gateways.py
    ├── urls.py
    ├── views.py
    ├── tasks.py
    ├── migrations/__init__.py
    ├── templates/{app_name}/
    └── tests/__init__.py
```

## Wiring

**`src/apps/{app_name}/__init__.py`:**
```python
import sys

from {app_name}.infrastructure import apps

# Django looks for <app>.apps. The config lives in infrastructure/.
sys.modules["{app_name}.apps"] = apps
```

**`src/apps/{app_name}/infrastructure/apps.py`:**
```python
from importlib import import_module

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class {AppName}Config(AppConfig):
    name = "{app_name}"
    label = "{app_name}"
    verbose_name = _("{App Name}")

    def import_models(self) -> None:
        # Models live in domain/models.py. Setting models_module keeps
        # post_migrate signals (permissions, content types) firing.
        self.models = self.apps.all_models[self.label]
        self.models_module = import_module("{app_name}.domain.models")

    def ready(self) -> None:
        import_module("{app_name}.infrastructure.admin")
```

For management commands, copy the `MANAGEMENT_COMMANDS` loop from `lending/infrastructure/apps.py`.

## Settings

1. Add `"{app_name}"` to `LOCAL_APPS` in `src/project_src/settings/base.py`.
2. Add `"{app_name}": "{app_name}.infrastructure.migrations"` to `MIGRATION_MODULES`.
3. Add `join_to_manage("apps/{app_name}/infrastructure/templates")` to `TEMPLATES[0]["DIRS"]`.
4. Add `"{app_name}.infrastructure"` to `autodiscover_tasks` in `src/project_src/celery.py` if the app has tasks.
5. Include `{app_name}.infrastructure.urls` in `src/project_src/urls.py` if the app has views.

## After creating

- Write the app's `CLAUDE.md` (max 30 lines).
- Run `make format` and `make test`.
