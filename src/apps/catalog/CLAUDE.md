## Catalog App

Owns books and the physical copies on the shelf. Knows nothing about who has a copy right now.

### Key Domain Invariants
- An ISBN is stored cleaned (`Isbn.from_raw`): no dashes, no spaces, upper-case X. Two spellings of one number are one book.
- A copy may go out on loan when it is not withdrawn and not damaged. That rule lives only in `CopyRepository.lendable_condition`. "On loan right now" is lending's business, not this rule.
- Copies are withdrawn, never deleted. Loans point at them with `PROTECT`.
- Barcodes are `<isbn>-<three-digit number>`, numbered on from the book's existing copies.
- Open Library fills in title and page count after a book is added. A blank title from Open Library keeps the librarian's title; a 404 changes nothing.

### Cross-App Dependencies
- **Imports from**: nothing.
- **Imported by**: lending, only in `lending.infrastructure.gateways.CatalogGateway` and lending's serializer (for `BARCODE_MAX_LENGTH`).

### Gotchas
- The details refresh is queued with `transaction.on_commit`, so the worker never runs before the row exists.
- `corelib.external.open_library.OpenLibraryClient` retries 429 and 5xx itself, then raises. `OpenLibraryGateway` lets that through, so the Celery task retries the rest.
