# Django DDD example

A small library system that shows one way to lay out a Django project with Domain-Driven Design and Clean Architecture. The business is deliberately boring. The point is where code goes and which way imports point.

Two bounded contexts, one Django app each:

- `catalog` owns books and the physical copies on the shelf.
- `lending` owns members, loans, renewals, late fees and due-date reminders. It needs to know about copies, but it asks the catalog through an interface and never imports catalog models in its use cases.

## Working with Claude Code

The repository is set up so an AI agent works inside the architecture instead of around it. The rules live in `CLAUDE.md`. The parts that must never be broken are checked by code rather than left to the prompt.

```
CLAUDE.md                      project rules, loaded every session
src/apps/<app>/CLAUDE.md       invariants of one bounded context
.claude/
├── settings.json              shared permissions and hooks
├── hooks/
│   ├── ddd_layer_guard.py     rejects imports that point outward
│   ├── auto_format.py         isort + black / djade on the edited file
│   └── safety_check.py        blocks destructive shell commands
├── skills/
│   ├── ddd-feature/           a feature across all layers, in order
│   └── new-app, new-model, new-usecase, new-gateway, new-service,
│       new-task, new-view, htmx-endpoint, new-admin, new-form
├── agents/
│   ├── ddd-reviewer.md        reviews a diff against the layer rules
│   └── test-writer.md         writes tests in the layer that owns the code
└── commands/
    └── review, check-architecture, lint, format
```

**Hooks make the architecture enforceable.** After every edit, `ddd_layer_guard.py` parses the file's imports. If a `domain/` or `application/` module imports `infrastructure/` or another app, the hook exits with code 2 and Claude gets the reason with the fix:

```
src/apps/lending/application/use_cases/borrow_copy.py:3: application imports
another app (catalog.domain.models). Add an interface in
lending/domain/interfaces.py and a gateway in lending/infrastructure/gateways.py.
```

The same script runs over the whole tree in `make lint` (`make architecture`), so humans and CI get the same check. `auto_format.py` formats only the file just edited, so diffs never carry style noise. `safety_check.py` stops `dropdb`, `DROP TABLE`, `migrate --fake`, force pushes, `git reset --hard` and `rm -rf` on root or home before they run.

**Skills carry the conventions.** Each skill describes one kind of change in this project's terms: where the file goes, what it looks like, how it is wired into the DI container and which tests it needs. Claude loads a skill when a request matches its description, or the user calls it by name (`/new-usecase`). `ddd-feature` ties them together: domain, then use case, then gateways, then delivery, then the finish checks.

**Subagents keep the review independent.** `ddd-reviewer` reads the diff with only the rules in front of it and reports one line per finding with severity and fix. It cannot edit files. `test-writer` adds tests in the layer that owns the code, using the existing `make_*` fixtures and stub gateways.

**Permissions match the risk.** Tests, lint and read-only git run without a prompt. Staging, committing, pushing and migrating always ask. Local and production settings files, which hold secrets, cannot be read at all.

A typical session:

```
> members can reserve a book that is on loan

  ddd-feature skill  ->  Reservation model + constraint, repository methods
                     ->  ReserveCopyUseCase + tests with a stub catalog
                     ->  LendingContainer factory, HTMX action, API
                     ->  hooks format each file and check its imports
                     ->  make lint, make test
                     ->  ddd-reviewer subagent  ->  findings fixed
```

## Running it

```bash
uv venv .venv && source .venv/bin/activate
make testing          # install test requirements
make test             # pytest on SQLite, no services needed

cp src/project_src/settings/local_template.py src/project_src/settings/local.py
# fill in SECRET_KEY and the Postgres credentials
make local            # install dev requirements and migrate
make server
make celery-worker    # needs Redis
```

`manage.py`, `wsgi.py` and `celery.py` default to `project_src.settings.local`. Production and CI pick their module with `DJANGO_SETTINGS_MODULE` (`project_src.settings.production`, `project_src.settings.ci`).

## Layout

```
src/
├── manage.py
├── project_src/                 settings, root urls, celery app, base templates
└── apps/
    ├── conftest.py              fixtures every app shares (make_user)
    ├── corelib/                 small helpers with no business meaning
    │   └── external/            HTTP clients for outside APIs
    └── <app>/
        ├── __init__.py          points Django at infrastructure/apps.py
        ├── CLAUDE.md            what the code cannot tell you
        ├── conftest.py          make_* fixtures for this app
        ├── domain/
        │   ├── models.py        Django models: the entities
        │   ├── managers.py      QuerySets and Repository managers
        │   ├── choices.py       TextChoices
        │   ├── exceptions.py    domain errors, each with a stable `code`
        │   ├── interfaces.py    ABCs for other apps and the outside world
        │   ├── settings.py      business numbers, with the reason for each
        │   ├── types.py         value objects and frozen dataclasses
        │   ├── services/        pure business logic, one class per file
        │   └── tests/
        ├── application/
        │   ├── use_cases/       one class per action, one public execute()
        │   └── tests/
        └── infrastructure/
            ├── apps.py          AppConfig
            ├── admin.py         Unfold admin
            ├── di.py            the container that builds use cases
            ├── gateways.py      implementations of domain interfaces
            ├── views.py         CBVs and HTMX fragments
            ├── api.py           DRF views
            ├── serializers.py   DRF serializers
            ├── forms.py
            ├── tasks.py         Celery tasks
            ├── urls.py
            ├── management/      management commands
            ├── migrations/
            ├── templates/<app>/
            └── tests/
```

## The layers

**Domain** holds the rules. Models, their QuerySets, the numbers the business runs on and any calculation that does not need the outside world. Domain code imports Django's ORM, because the models are the entities here. It does not import from `application/` or `infrastructure/`, and it does not import another app. A foreign key to another app's model, named by string (`"catalog.Copy"`), is allowed: it keeps integrity in the database without an import.

**Application** holds the actions a user or a schedule can take: borrow a copy, return it, send the reminders. A use case is a class with one public method, `execute()`, and small private steps. It reads and writes through the model's repository manager, raises domain errors, and returns either a model or a frozen dataclass built for the caller. It does not know about requests, templates, Celery or email.

**Infrastructure** is everything that touches the edges: HTTP, admin, Celery, email, outside APIs, other apps. It builds use cases through the app's DI container and turns their answers into responses.

Imports point inward only:

```
infrastructure  ->  application  ->  domain
```

## Conventions

### Repository managers

Every model has two managers:

```python
objects = models.Manager()
repository = LoanRepository()
```

`objects` stays plain for Django internals, fixtures and the admin. `repository` is where every query with business meaning lives. Use cases, views and tasks never build an ORM filter themselves. They call a named method, such as `Loan.repository.member_has_overdue(...)`.

A rule that more than one query needs is written once. `CopyRepository.lendable_condition()` returns the `Q` object that says which copies may go out. `CopyQuerySet.lendable()` and the book search annotation both use it.

Repository methods that feed a page return `.values()` rows with plain keys (`book_title`, not `copy__book__title`), so callers never depend on the join path.

### Use cases

```python
class ReturnCopyUseCase:
    def __init__(self, *, late_fees: LateFeeCalculator) -> None:
        self._late_fees = late_fees

    def execute(self, *, user, loan_id: int, today: date) -> ReturnReceipt:
        ...
```

- Arguments are keyword-only.
- Dependencies come in through `__init__`, typed as interfaces or domain services.
- "Today" is an argument. The caller reads the clock, so tests pass a fixed date.
- Checks come before writes, and the database has the last word. `BorrowCopyUseCase` checks that a copy is free, and a partial unique index refuses a second open loan if two desks pass the check at once. The use case turns that `IntegrityError` into `CopyAlreadyOnLoan`.
- Limits that requests can race on sit in a conditional UPDATE. `LoanRepository.extend()` only renews while `renewal_count < MAX_RENEWALS`.

### Read models

A page or an API never receives a queryset. A use case returns a frozen dataclass such as `MyLoansReport` with `LoanRow` items. Anything that depends on today (`days_left`, `is_overdue`, `can_renew`) is worked out there, so templates and serializers only format.

### Domain errors

Every app has a base error and one subclass per refusal. Each has a stable `code`:

```python
class LoanLimitReached(LendingError):
    code = "loan_limit_reached"
```

The DRF view returns `{"error": exc.code}`. The web views map the class to a translated message. Neither parses exception text.

### Interfaces and gateways

An interface in `domain/interfaces.py` is written for each thing the app needs from outside its own models:

- another app (`lending.CatalogInterface`, implemented by `CatalogGateway`, the only lending module that imports catalog models),
- an outside service (`catalog.BookDetailsInterface`, implemented by `OpenLibraryGateway` on top of `OpenLibraryClient`),
- a side effect (`lending.ReminderSenderInterface`, implemented by `EmailReminderSender`).

Tests pass small stub classes that subclass the interface. No mocking library is needed for use case tests.

### Clients and gateways

An outside API gets two classes with one job each:

- A **client** in `corelib/external/` speaks HTTP. It owns the session, the timeout and the retry policy, and returns the API's own shapes (`OpenLibraryEdition`). It knows nothing about any app, so two apps can share it.
- A **gateway** in the app's `infrastructure/gateways.py` implements the domain interface. It takes the client in `__init__` and turns the API's shapes into domain types (`BookDetails`).

The DI container joins them: `OpenLibraryGateway(client=OpenLibraryClient())`. Client tests patch the session. Gateway tests pass a stub client and never touch HTTP.

The app's own models are not hidden behind an interface. That is a deliberate trade: the ORM is the persistence layer and the entity at once, and wrapping it buys nothing a Django project uses.

### DI container

```python
class LendingContainer:
    @staticmethod
    def get_borrow_copy_use_case() -> BorrowCopyUseCase:
        return BorrowCopyUseCase(catalog=CatalogGateway())
```

Views, tasks, API views and management commands all ask the container. Nothing outside `di.py` picks a concrete gateway.

### Domain services

Pure logic that does not belong to one model lives in `domain/services/`. `LateFeeCalculator` takes dates and a frozen `LateFeePolicy` and returns a `LateFee`. It has no database and no clock, so its tests are plain function calls.

### Numbers

Business numbers sit in `domain/settings.py` with a comment on why each one is what it is. Code never repeats a literal.

## Making Django find things outside the usual places

Models, admin, migrations, templates, tasks and commands all live in `domain/` or `infrastructure/`, so Django needs to be told where to look.

| What | Where Django looks | How this project points it elsewhere |
|---|---|---|
| AppConfig | `<app>/apps.py` | `<app>/__init__.py` aliases `sys.modules["<app>.apps"]` |
| Models | `<app>/models.py` | `AppConfig.import_models()` imports `domain.models` and sets `models_module` |
| Admin | `<app>/admin.py` | `AppConfig.ready()` imports `infrastructure.admin` |
| Migrations | `<app>/migrations/` | `MIGRATION_MODULES` in settings |
| Templates | `<app>/templates/` | each app's `infrastructure/templates` is listed in `TEMPLATES["DIRS"]` |
| Celery tasks | `<app>/tasks.py` | `autodiscover_tasks` gets `<app>.infrastructure` |
| Commands | `<app>/management/commands/` | `AppConfig.ready()` registers each command name |

Setting `models_module` matters. Without it Django thinks the app has no models and skips `post_migrate` for it, so no permissions or content types are created.

## Tests

Tests sit next to the layer they test: `domain/tests/`, `application/tests/`, `infrastructure/tests/`. Fixtures are `make_*` factories in each app's `conftest.py`.

- Domain tests cover value objects, services and repository queries.
- Application tests run use cases against a real test database with stub gateways.
- Infrastructure tests go through the test client, the API client, Celery in eager mode and the locmem email backend.

`make test` runs on in-memory SQLite. CI runs the same suite on Postgres through `settings/ci.py`.
