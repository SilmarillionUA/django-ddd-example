from django.urls import reverse

import pytest


@pytest.mark.parametrize("model_name", ["member", "loan"])
def test_changelist_loads(
    admin_client, make_member, make_copy, make_loan, model_name
):
    make_loan(member=make_member(), copy=make_copy())

    response = admin_client.get(
        reverse(f"admin:lending_{model_name}_changelist")
    )

    assert response.status_code == 200
