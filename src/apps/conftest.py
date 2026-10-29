from django.contrib.auth import get_user_model

import pytest

User = get_user_model()


@pytest.fixture
def make_user(db):
    def _make(username="reader", email="reader@example.com", is_staff=False):
        return User.objects.create_user(
            username=username,
            email=email,
            password="x",
            is_staff=is_staff,
        )

    return _make
