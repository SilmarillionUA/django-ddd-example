from catalog.application.use_cases.refresh_book_details import (
    RefreshBookDetailsUseCase,
)
from catalog.domain.interfaces import BookDetailsInterface
from catalog.domain.types import BookDetails, Isbn


class StubBookDetails(BookDetailsInterface):
    def __init__(self, details: BookDetails | None) -> None:
        self._details = details
        self.asked: list[Isbn] = []

    def fetch(self, *, isbn: Isbn) -> BookDetails | None:
        self.asked.append(isbn)
        return self._details


def refresh(*, book_id, details):
    use_case = RefreshBookDetailsUseCase(
        book_details=StubBookDetails(details=details)
    )

    return use_case.execute(book_id=book_id)


def test_details_from_outside_are_stored(make_book):
    book_obj = make_book(title="typed title")

    updated = refresh(
        book_id=book_obj.pk,
        details=BookDetails(title="Real Title", page_count=412),
    )

    book_obj.refresh_from_db()
    assert updated
    assert (book_obj.title, book_obj.page_count) == ("Real Title", 412)


def test_blank_outside_title_keeps_typed_title(make_book):
    book_obj = make_book(title="typed title")

    refresh(book_id=book_obj.pk, details=BookDetails(page_count=10))

    book_obj.refresh_from_db()
    assert book_obj.title == "typed title"


def test_unknown_to_outside_source_changes_nothing(make_book):
    book_obj = make_book()

    assert not refresh(book_id=book_obj.pk, details=None)


def test_deleted_book_is_skipped(db):
    assert not refresh(book_id=404, details=BookDetails(title="x"))
