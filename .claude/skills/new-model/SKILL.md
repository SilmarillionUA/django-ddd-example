---
name: new-model
description: Add a Django model with its QuerySet and repository manager in the domain layer. Use when a feature needs a new table or entity.
---

# Create a new model with a repository manager

Create a model with the name the user gives.

## Model (`domain/models.py`)

- `gettext_lazy as _` for verbose names.
- `created_at` (`auto_now_add`) and `updated_at` (`auto_now`).
- `objects = models.Manager()` and `repository = {Model}Repository()`.
- `related_name` on every relation. A relation to another app uses the string name (`"catalog.Copy"`).
- `Meta` with `ordering`, `verbose_name`, `verbose_name_plural`, and `constraints` for every invariant the database can hold (unique, partial unique, check). Prefix constraint names with the app label.
- `__str__` and `get_admin_url()`.
- A docstring that says what one row means and any rule about its lifetime (closed, withdrawn, never deleted).
- Lengths and limits come from `domain/settings.py`.

## Manager (`domain/managers.py`)

```python
class {Model}QuerySet(models.QuerySet):
    def still_open(self) -> "{Model}QuerySet":
        return self.filter(...)


class {Model}Repository(models.Manager):
    def get_queryset(self) -> {Model}QuerySet:
        return {Model}QuerySet(self.model, using=self._db)

    def open_count_for_member(self, *, member_id: int) -> int:
        return self.get_queryset().still_open().filter(member_id=member_id).count()
```

- Chainable filters on the QuerySet, named in domain words.
- Business questions on the Repository, keyword-only, returning a bool, a count, one object or `None`, or `.values()` rows with plain keys.
- A condition that several queries share is a `Q` builder written once.
- `TYPE_CHECKING` imports for model types.

## Admin

Register it in `infrastructure/admin.py` (see `/new-admin`).

## After creating

- `python src/manage.py makemigrations`
- `make format`
