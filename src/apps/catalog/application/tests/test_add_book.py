import pytest

from catalog.application.use_cases.add_book import AddBookUseCase
from catalog.domain.exceptions import (
    CopyCountOutOfRange,
    DuplicateIsbn,
    InvalidIsbn,
)
from catalog.domain.models import Book
from catalog.domain.settings import MAX_COPIES_PER_BOOK_REQUEST


def add_book(**overrides):
    arguments = {
        "raw_isbn": "978-0-00-000000-1",
        "title": "Dune",
        "author": "Herbert",
        "copy_count": 2,
        **overrides,
    }

    return AddBookUseCase().execute(**arguments)


@pytest.mark.django_db
def test_book_is_stored_with_clean_isbn_and_copies():
    book_obj = add_book()

    assert book_obj.isbn == "9780000000001"
    assert book_obj.copies.count() == 2


@pytest.mark.django_db
def test_same_isbn_typed_differently_is_a_duplicate():
    add_book(raw_isbn="9780000000001")

    with pytest.raises(DuplicateIsbn):
        add_book(raw_isbn="978 0 00 000000 1")


@pytest.mark.django_db
def test_invalid_isbn_writes_nothing():
    with pytest.raises(InvalidIsbn):
        add_book(raw_isbn="nope")

    assert not Book.objects.exists()


@pytest.mark.django_db
@pytest.mark.parametrize("copy_count", [0, MAX_COPIES_PER_BOOK_REQUEST + 1])
def test_copy_count_outside_limits_is_refused(copy_count):
    with pytest.raises(CopyCountOutOfRange):
        add_book(copy_count=copy_count)
