from dataclasses import dataclass
from http import HTTPStatus

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


@dataclass(frozen=True)
class OpenLibraryEdition:
    title: str = ""
    number_of_pages: int | None = None


class OpenLibraryClient:
    """
    HTTP transport for the Open Library API, with no business meaning.

    It owns the session, the timeout and the retry policy, and returns
    Open Library's own shapes. Turning them into domain types is the
    gateway's job. A 404 is a normal answer and comes back as None.
    Every other failure raises once the retries run out.
    """

    BASE_URL = "https://openlibrary.org"
    ISBN_PATH = "/isbn/{isbn}.json"
    TIMEOUT_SECONDS = 10
    RETRY_POLICY = Retry(
        total=3,
        backoff_factor=1.0,
        status_forcelist=[
            HTTPStatus.TOO_MANY_REQUESTS,
            HTTPStatus.INTERNAL_SERVER_ERROR,
            HTTPStatus.BAD_GATEWAY,
            HTTPStatus.SERVICE_UNAVAILABLE,
            HTTPStatus.GATEWAY_TIMEOUT,
        ],
        allowed_methods=["GET"],
    )

    def __init__(self) -> None:
        self._session = requests.Session()
        self._session.mount(
            "https://", HTTPAdapter(max_retries=self.RETRY_POLICY)
        )

    def edition_by_isbn(self, *, isbn: str) -> OpenLibraryEdition | None:
        response = self._session.get(
            self.BASE_URL + self.ISBN_PATH.format(isbn=isbn),
            timeout=self.TIMEOUT_SECONDS,
        )
        if response.status_code == HTTPStatus.NOT_FOUND:
            return None

        response.raise_for_status()
        payload = response.json()

        return OpenLibraryEdition(
            title=payload.get("title") or "",
            number_of_pages=payload.get("number_of_pages"),
        )
