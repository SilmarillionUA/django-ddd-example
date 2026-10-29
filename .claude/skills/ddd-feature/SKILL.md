---
name: ddd-feature
description: Build a feature end to end across the domain, application and infrastructure layers, in the order this project uses. Use when a request adds behavior, such as "members can reserve a book", rather than a single file.
---

# Build a feature through the layers

Work inside out. Each step leaves the code runnable, and the tests for a layer are written with that layer.

## 1. Find the bounded context

Read the app's `CLAUDE.md`. If the feature belongs to no existing app, stop and use the `new-app` skill. If it needs data another app owns, plan an interface for it now (step 4). Never import the other app's models outside a gateway.

## 2. Domain

- New table: `new-model` skill. Put every invariant the database can hold into `Meta.constraints`.
- New query: a named method on the repository manager. Reuse the existing `Q` builders and QuerySet filters.
- New numbers: `domain/settings.py`, with a comment saying why.
- Each refusal: a subclass of the app's base error with a stable `code`.
- Pure calculation: `new-service` skill.
- Tests: `domain/tests/`, one per rule.

## 3. Application

- One use case per action: `new-usecase` skill.
- The date comes in as `today=`. Dependencies come in through `__init__`.
- Return a model or a frozen read-model dataclass. Work out everything that depends on today there.
- Tests: `application/tests/`, with stub subclasses of each interface.

## 4. Gateways

For each outside need, use the `new-gateway` skill: interface in `domain/interfaces.py`, implementation in `infrastructure/gateways.py`, wiring in `infrastructure/di.py`.

## 5. Delivery

Pick what the request needs, each through the container:

- Page: `new-view` skill, and `htmx-endpoint` for fragments and actions.
- API: a DRF view in `infrastructure/api.py` that returns `{"error": exc.code}` on domain errors.
- Background or periodic: `new-task` skill.
- Staff tools: `new-admin` skill.

Tests: `infrastructure/tests/`.

## 6. Finish

1. `python src/manage.py makemigrations` if models changed.
2. Update the app's `CLAUDE.md` if an invariant or a cross-app dependency changed.
3. `make format`, `make lint`, `make test`. `make lint` includes the layer check.
4. Ask the `ddd-reviewer` subagent to review the diff, and fix what it reports.

Stop there. Do not stage or commit.
