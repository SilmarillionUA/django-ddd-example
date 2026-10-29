import pytest

from catalog.domain.choices import CopyCondition
from catalog.domain.models import Book, Copy


@pytest.fixture
def make_book(db):
    def _make(isbn="9780000000001", title="Test Book", author="Test Author"):
        return Book.objects.create(isbn=isbn, title=title, author=author)

    return _make


@pytest.fixture
def make_copy(db):
    def _make(
        *,
        book,
        barcode="9780000000001-001",
        condition=CopyCondition.GOOD,
        is_withdrawn=False,
    ):
        return Copy.objects.create(
            book=book,
            barcode=barcode,
            condition=condition,
            is_withdrawn=is_withdrawn,
        )

    return _make
