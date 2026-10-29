from catalog.application.use_cases.search_books import SearchBooks


def test_report_marks_full_page(make_book, make_copy):
    for number in range(3):
        make_book(isbn=f"978000000000{number}", title=f"Book {number}")

    report = SearchBooks().execute(limit=2)

    assert len(report.rows) == 2
    assert report.is_full_page


def test_book_without_lendable_copies_is_not_lendable(make_book):
    make_book()

    report = SearchBooks().execute(search="  test ")

    assert report.search == "test"
    assert not report.rows[0].is_lendable
