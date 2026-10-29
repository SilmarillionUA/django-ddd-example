from catalog.domain.choices import CopyCondition
from catalog.domain.models import Book, Copy


def test_search_rows_count_only_lendable_copies(make_book, make_copy):
    book_obj = make_book()
    make_copy(book=book_obj, barcode="a")
    make_copy(book=book_obj, barcode="b", condition=CopyCondition.DAMAGED)
    make_copy(book=book_obj, barcode="c", is_withdrawn=True)

    rows = list(Book.repository.search_rows(term="", limit=10))

    assert [row.get("lendable_copies") for row in rows] == [1]


def test_search_rows_match_title_author_and_isbn(make_book):
    make_book(isbn="9780000000001", title="Dune", author="Herbert")
    make_book(isbn="9780000000002", title="Emma", author="Austen")

    def titles(term):
        return [
            row.get("title")
            for row in Book.repository.search_rows(term=term, limit=10)
        ]

    assert titles("dun") == ["Dune"]
    assert titles("austen") == ["Emma"]
    assert titles("0002") == ["Emma"]


def test_add_copies_continues_numbering(make_book):
    book_obj = make_book(isbn="9780000000001")

    Copy.repository.add_copies(book=book_obj, count=2)
    Copy.repository.add_copies(book=book_obj, count=1)

    assert list(
        Copy.objects.filter(book=book_obj).values_list("barcode", flat=True)
    ) == ["9780000000001-001", "9780000000001-002", "9780000000001-003"]


def test_damaged_copy_is_not_lendable(make_book, make_copy):
    copy_obj = make_copy(book=make_book(), condition=CopyCondition.DAMAGED)

    assert not Copy.repository.is_lendable(copy_id=copy_obj.pk)
