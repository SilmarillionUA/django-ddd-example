from http import HTTPStatus

import pytest
import requests

from corelib.external.open_library import OpenLibraryClient, OpenLibraryEdition

ISBN = "9780000000001"


@pytest.fixture
def client_with_response(mocker):
    def _make(*, status_code, payload=None):
        response = requests.Response()
        response.status_code = status_code
        response.json = mocker.Mock(return_value=payload or {})

        client = OpenLibraryClient()
        get = mocker.patch.object(
            client._session, "get", return_value=response
        )
        return client, get

    return _make


@pytest.mark.unit
def test_edition_is_read_from_payload(client_with_response):
    client, get = client_with_response(
        status_code=HTTPStatus.OK,
        payload={"title": "Dune", "number_of_pages": 412},
    )

    edition = client.edition_by_isbn(isbn=ISBN)

    assert edition == OpenLibraryEdition(title="Dune", number_of_pages=412)
    assert get.call_args.args[0] == f"https://openlibrary.org/isbn/{ISBN}.json"
    assert (
        get.call_args.kwargs.get("timeout")
        == OpenLibraryClient.TIMEOUT_SECONDS
    )


@pytest.mark.unit
def test_missing_fields_default(client_with_response):
    client, _ = client_with_response(status_code=HTTPStatus.OK, payload={})

    assert client.edition_by_isbn(isbn=ISBN) == OpenLibraryEdition()


@pytest.mark.unit
def test_unknown_isbn_is_none(client_with_response):
    client, _ = client_with_response(status_code=HTTPStatus.NOT_FOUND)

    assert client.edition_by_isbn(isbn=ISBN) is None


@pytest.mark.unit
def test_server_error_raises(client_with_response):
    client, _ = client_with_response(status_code=HTTPStatus.BAD_GATEWAY)

    with pytest.raises(requests.HTTPError):
        client.edition_by_isbn(isbn=ISBN)
