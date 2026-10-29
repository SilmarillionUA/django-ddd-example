from django.urls import reverse

import pytest


@pytest.mark.parametrize("model_name", ["book", "copy"])
def test_changelist_loads(admin_client, make_book, make_copy, model_name):
    make_copy(book=make_book())

    response = admin_client.get(
        reverse(f"admin:catalog_{model_name}_changelist")
    )

    assert response.status_code == 200


def test_book_page_shows_copies_inline(admin_client, make_book, make_copy):
    book_obj = make_book()
    make_copy(book=book_obj, barcode="inline-copy")

    response = admin_client.get(book_obj.get_admin_url())

    assert b"inline-copy" in response.content
