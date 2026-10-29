from dataclasses import dataclass, field

from catalog.domain.models import Book
from catalog.domain.settings import MAX_BOOKS_ON_PAGE


@dataclass(frozen=True)
class BookRow:
    book_id: int
    isbn: str
    title: str
    author: str
    lendable_copies: int

    @property
    def is_lendable(self) -> bool:
        return self.lendable_copies > 0


@dataclass(frozen=True)
class BookSearchReport:
    """
    One page of the catalog for a search term.

    `is_full_page` tells the page that more books matched than it
    shows, so it can ask the reader to narrow the search.
    """

    search: str = ""
    max_books: int = MAX_BOOKS_ON_PAGE
    rows: list[BookRow] = field(default_factory=list)

    @property
    def has_rows(self) -> bool:
        return bool(self.rows)

    @property
    def is_full_page(self) -> bool:
        return len(self.rows) >= self.max_books


class SearchBooks:
    def execute(
        self, *, search: str = "", limit: int = MAX_BOOKS_ON_PAGE
    ) -> BookSearchReport:
        term = search.strip()

        return BookSearchReport(
            search=term,
            max_books=limit,
            rows=[
                self._row(values=values)
                for values in Book.repository.search_rows(
                    term=term, limit=limit
                )
            ],
        )

    @staticmethod
    def _row(*, values: dict) -> BookRow:
        return BookRow(
            book_id=values.get("id"),
            isbn=values.get("isbn"),
            title=values.get("title"),
            author=values.get("author"),
            lendable_copies=values.get("lendable_copies"),
        )
