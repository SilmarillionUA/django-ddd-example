from django.urls import reverse

import pytest

from catalog.domain.models import Book

HTMX_HEADERS = {"HTTP_HX_REQUEST": "true"}


def test_list_page_shows_books(client, make_book):
    make_book(title="Dune")

    response = client.get(reverse("catalog:book_list"))

    assert response.status_code == 200
    assert b"Dune" in response.content


def test_table_fragment_filters_by_search(client, make_book):
    make_book(isbn="9780000000001", title="Dune")
    make_book(isbn="9780000000002", title="Emma")

    response = client.get(
        reverse("catalog:book_table"), {"q": "emm"}, **HTMX_HEADERS
    )

    assert b"Emma" in response.content
    assert b"Dune" not in response.content


def test_add_book_is_staff_only(client, make_user):
    client.force_login(make_user())

    response = client.get(reverse("catalog:book_create"))

    assert response.status_code == 403


@pytest.mark.django_db(transaction=True)
def test_added_book_queues_details_refresh(client, make_user, mocker):
    delay = mocker.patch(
        "catalog.infrastructure.views.refresh_book_details.delay"
    )
    client.force_login(make_user(is_staff=True))

    response = client.post(
        reverse("catalog:book_create"),
        {"isbn": "978-0-00-000000-1", "title": "Dune", "copy_count": 1},
    )

    book_obj = Book.objects.get()
    assert response.status_code == 302
    delay.assert_called_once_with(book_id=book_obj.pk)


def test_duplicate_isbn_comes_back_on_the_form(client, make_user, make_book):
    make_book(isbn="9780000000001")
    client.force_login(make_user(is_staff=True))

    response = client.post(
        reverse("catalog:book_create"),
        {"isbn": "9780000000001", "title": "Dune", "copy_count": 1},
    )

    assert response.status_code == 200
    assert "isbn" in response.context["form"].errors
