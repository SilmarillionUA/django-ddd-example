---
name: new-form
description: Add a Django form that checks input shape only and leaves domain rules to the use case.
---

# Create a form

Create a form with the name the user gives in the app's `infrastructure/forms.py`.

## Rules

- A form checks the shape of input only: required, length, type, range.
- Domain rules (valid ISBN, already taken, limits) are decided by the use case. The view catches the domain error and calls `form.add_error()` (see `BookCreateView`).
- Prefer `forms.Form` feeding a use case over a `ModelForm` that saves directly.
- Bootstrap widget classes: `form-control`, `form-select`, `form-check-input`.
- `gettext_lazy` labels. Limits from `domain/settings.py`.

## After creating

- `make format`
