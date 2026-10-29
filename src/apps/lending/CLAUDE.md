## Lending App

Owns library members, loans, renewals, late fees and due-date reminders.

### Key Domain Invariants
- A user borrows only with a `Member` row, created by a librarian. Logging in is not enough.
- Member checks run before copy checks: suspended, then any overdue loan, then the open-loan limit.
- One open loan per copy. The use case checks first and the partial unique index `lending_one_open_loan_per_copy` settles races.
- A loan is closed by setting `returned_on`, never deleted.
- Renewing extends from the old due date, not from today. Overdue loans cannot be renewed. The renewal limit sits in the UPDATE, so double clicks cannot pass it.
- The late fee is computed once, when the loan closes, and stored. Changing the fee rules never rewrites past charges.
- A member only ever sees or acts on their own loans: `open_for_user` and `rows_for_user` filter by user.
- Each loan gets at most one reminder. It is marked right after its email is sent, so a retry never sends twice.

### Cross-App Dependencies
- **Imports from**: catalog, only through `CatalogGateway` (and the `"catalog.Copy"` foreign key).
- **Imported by**: nothing.

### Gotchas
- The HTMX loan table carries its own messages (`show_messages`). The full page shows them in the layout.
- The `send_due_reminders` command and the Celery beat task run the same use case.
