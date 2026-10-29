from django.test import RequestFactory

import pytest

from corelib.http import is_htmx


@pytest.mark.unit
def test_htmx_request_is_detected_by_header():
    request = RequestFactory().get("/", HTTP_HX_REQUEST="true")

    assert is_htmx(request)


@pytest.mark.unit
def test_plain_request_is_not_htmx():
    request = RequestFactory().get("/")

    assert not is_htmx(request)
