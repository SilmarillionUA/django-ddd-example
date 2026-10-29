# 0001. Each Django app is a bounded context with domain, application and infrastructure layers

- Status: Accepted
- Date: 2026-10-29

## Context

Default Django apps put models, views, forms and business rules side by side. As an app grows, rules end up in views, querysets are rebuilt by hand in several places, and one app reaches into another's models wherever it is convenient. Tests then need the whole stack to check one rule.

Full DDD with a separate persistence layer and mapped entities fights the ORM, and on a Django project it doubles the code for little gain.

## Decision

Each Django app is one bounded context, split into three layers:

- `domain/` holds Django models as entities, repository managers for queries, value objects, domain services, errors, interfaces and business constants.
- `application/` holds one use case class per action, with a single `execute()`.
- `infrastructure/` holds views, API, admin, tasks, commands, templates, gateways and a DI container.

Imports point inward only. An app never imports another app outside its gateways. The app's own models are not hidden behind interfaces: the ORM is accepted as the persistence layer.

## Consequences

- A rule lives in one place and is tested at the layer it belongs to. Use case tests need a database but no HTTP and no mocks beyond stub gateways.
- Swapping an outside service or splitting an app out touches one gateway and one container method.
- Django needs extra wiring to find models, admin, migrations, templates, tasks and commands outside the default paths. The README lists each one.
- More files per feature than plain Django. Small apps carry some ceremony.
