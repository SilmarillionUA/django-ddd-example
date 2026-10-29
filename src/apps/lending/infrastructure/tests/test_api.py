from django.urls import reverse

import pytest
from rest_framework.test import APIClient

URL = reverse("lending_api:my_loans")


@pytest.fixture
def api_client():
    return APIClient()


def test_lists_open_loans(api_client, make_member, make_copy, make_loan):
    member_obj = make_member()
    make_loan(member=member_obj, copy=make_copy(title="Dune"))
    api_client.force_authenticate(member_obj.user)

    payload = api_client.get(URL).json()

    assert payload.get("is_member")
    assert [loan.get("book_title") for loan in payload.get("loans")] == [
        "Dune"
    ]


def test_borrow_returns_created(api_client, make_member, make_copy):
    member_obj = make_member()
    api_client.force_authenticate(member_obj.user)

    response = api_client.post(URL, {"barcode": make_copy().barcode})

    assert response.status_code == 201


def test_domain_error_returns_stable_code(api_client, make_user):
    api_client.force_authenticate(make_user())

    response = api_client.post(URL, {"barcode": "anything"})

    assert response.status_code == 400
    assert response.json() == {"error": "membership_required"}


def test_anonymous_is_refused(api_client, db):
    assert api_client.get(URL).status_code == 403
