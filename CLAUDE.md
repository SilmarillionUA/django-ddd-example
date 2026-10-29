## Project Structure

- Apps live in `src/apps/`. Each app is one bounded context with three layers: `domain/`, `application/`, `infrastructure/`.
- Imports point inward only: infrastructure imports application and domain, application imports domain, domain imports neither.
- A domain or application module never imports another app. Cross-app needs go through an ABC in `domain/interfaces.py` and a gateway in `infrastructure/gateways.py`. A foreign key by string name (`"catalog.Copy"`) is fine.
- Models, managers, interfaces, choices, exceptions, value objects and business constants live in `domain/`.
- ORM query building belongs on the model's QuerySet or repository manager in `domain/managers.py`. Never inline a filter in a use case, view, task or command. Compose the existing helpers instead of repeating a condition.
- Each model has `objects = models.Manager()` and `repository = <Model>Repository()`.
- A rule that several queries need is written once, as a `Q` builder on the repository (see `CopyRepository.lendable_condition`).
- Use cases live in `application/use_cases/`, one action per file. Use cases and domain services are classes with one public `execute()` and small private helpers.
- Use cases take keyword-only arguments. Dependencies come in through `__init__`. The current date or time comes in as an argument (`today=`), never read inside.
- Use cases return a model or a frozen dataclass read model (`MyLoansReport`, `LoanRow`). Anything that depends on today is computed there, not in templates or serializers.
- Domain errors subclass the app's base error and carry a stable `code`. The API returns the code; web views map the class to a translated message.
- Checks run before writes, and the database enforces the invariant too (unique index, check constraint, conditional UPDATE). Turn the resulting `IntegrityError` into the domain error, in a narrow try block.
- Domain services in `domain/services/` are pure: no ORM, no clock. Configuration is a frozen dataclass.
- Business numbers live in `domain/settings.py` with a comment on why.
- Views, admin, forms, serializers, API views, tasks, commands, templates, gateways and the DI container live in `infrastructure/`.
- Each app has a DI container in `infrastructure/di.py` (e.g. `LendingContainer`) with `@staticmethod` factories. Views, tasks and commands get use cases from it and never build gateways themselves.
- API output goes through DRF `serializers.Serializer` subclasses with `to_representation()`. Request-scoped state arrives via serializer `context`.
- Shared helpers with no business meaning go in `corelib`.
- An outside API is split in two. The client in `corelib/external/` owns HTTP (session, timeout, retries) and returns the API's shapes. The gateway in `infrastructure/gateways.py` takes the client in `__init__` and maps those shapes to domain types. Gateways never call `requests` themselves.

## Wiring an app

- `<app>/__init__.py` aliases `sys.modules["<app>.apps"]` to `infrastructure/apps.py`.
- The AppConfig overrides `import_models()` to load `domain/models.py` and set `models_module`, and imports `infrastructure.admin` in `ready()`.
- Add the app to `LOCAL_APPS`, `MIGRATION_MODULES` and `TEMPLATES["DIRS"]` in `settings/base.py`, and to `autodiscover_tasks` in `project_src/celery.py` if it has tasks.
- Management commands are registered by name in `ready()` (see `lending/infrastructure/apps.py`).

## Commands

- `make test` runs pytest on SQLite (`settings/testing.py`).
- `make server`, `make db`, `make celery-worker`, `make celery-beat`.
- `make format` runs isort, black and djade. `make lint` runs flake8, the DDD layer check (`make architecture`) and the black and isort checks.

## Testing

- pytest with `pytest-django`. Tests go in `{layer}/tests/` inside each app.
- `make_*` factory fixtures in the app's `conftest.py`. `make_user` is shared in `src/apps/conftest.py`.
- Use case tests pass stub classes that subclass the domain interface. Patch only at the infrastructure edge (HTTP calls, `.delay`).
- Markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`.

## Instructions

- Use `structlog.get_logger(__name__)` in infrastructure. Use `logging.getLogger(__name__)` in domain and application.
- Absolute imports from the app name (`from lending.domain.models import Loan`), never relative.
- Top-level imports only, except `TYPE_CHECKING` blocks and `import_module` in `AppConfig`.
- No magic numbers or strings. Name them at module level.
- Narrow try/except blocks, one failure mode each. Never hide errors.
- Prefer `filter().first()` over try/except `DoesNotExist`, and `dict.get()` over square brackets unless a missing key should raise.
- Named arguments for calls with two or more arguments that could be swapped.
- Comments explain why, never what. Docstrings on classes and functions whose contract is not obvious.
- No inline CSS. Bootstrap classes first. `js-` prefix for classes used by JavaScript, never targeted by CSS.
- User-facing text lives in templates with `{% translate %}`, or in `gettext` for messages.
- `select_related` and `prefetch_related` wherever a list touches a relation.

## Per-app CLAUDE.md

Each app has a `CLAUDE.md` of at most 30 lines: what the context owns, invariants the code does not show, cross-app dependencies, gotchas. Do not list files or restate this file. Update it when the rules change.

## Claude Code setup

- Hooks run on every edit: the file is formatted, then `ddd_layer_guard.py` rejects imports that point outward. Fix the import it reports; do not work around the guard.
- Destructive shell commands are blocked by `safety_check.py`. Ask the user instead of retrying.
- For a feature that spans layers, follow the `ddd-feature` skill. Single pieces have their own skills (`new-usecase`, `new-gateway`, and so on).
- Before handing work back, run `make lint` and `make test`, then ask the `ddd-reviewer` subagent for a review.
