from django.urls import reverse

from lending.domain.models import Loan

HTMX_HEADERS = {"HTTP_HX_REQUEST": "true"}


def test_page_tells_non_member_how_to_get_a_card(client, make_user):
    client.force_login(make_user())

    response = client.get(reverse("lending:my_loans"))

    assert not response.context["my_loans"].is_member


def test_htmx_borrow_returns_table_with_message(
    client, make_member, make_copy
):
    member_obj = make_member()
    copy_obj = make_copy(title="Dune")
    client.force_login(member_obj.user)

    response = client.post(
        reverse("lending:borrow"),
        {"barcode": copy_obj.barcode},
        **HTMX_HEADERS,
    )

    assert response.status_code == 200
    assert b"Dune" in response.content
    assert b"Enjoy the book." in response.content


def test_plain_post_redirects_back_to_page(client, make_member, make_copy):
    member_obj = make_member()
    client.force_login(member_obj.user)

    response = client.post(
        reverse("lending:borrow"), {"barcode": make_copy().barcode}
    )

    assert response.status_code == 302
    assert Loan.objects.count() == 1


def test_domain_error_becomes_a_message(client, make_member):
    client.force_login(make_member().user)

    response = client.post(
        reverse("lending:borrow"), {"barcode": "nothing"}, **HTMX_HEADERS
    )

    assert b"No copy has this barcode." in response.content


def test_return_closes_the_loan(client, make_member, make_copy, make_loan):
    member_obj = make_member()
    loan_obj = make_loan(member=member_obj, copy=make_copy())
    client.force_login(member_obj.user)

    client.post(
        reverse("lending:return_loan", kwargs={"loan_id": loan_obj.pk}),
        **HTMX_HEADERS,
    )

    loan_obj.refresh_from_db()
    assert not loan_obj.is_open


def test_anonymous_user_is_sent_to_login(client):
    response = client.get(reverse("lending:my_loans"))

    assert response.status_code == 302
    assert reverse("login") in response.url
