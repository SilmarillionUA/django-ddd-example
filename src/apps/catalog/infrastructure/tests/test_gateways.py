import pytest

from catalog.domain.types import BookDetails, Isbn
from catalog.infrastructure.gateways import OpenLibraryGateway
from corelib.external.open_library import OpenLibraryClient, OpenLibraryEdition

ISBN = Isbn(value="9780000000001")


class StubClient(OpenLibraryClient):
    """Answers from memory. The client's own tests cover the HTTP."""

    def __init__(self, *, edition: OpenLibraryEdition | None) -> None:
        self._edition = edition
        self.asked: list[str] = []

    def edition_by_isbn(self, *, isbn: str) -> OpenLibraryEdition | None:
        self.asked.append(isbn)
        return self._edition


@pytest.mark.unit
def test_edition_becomes_book_details():
    client = StubClient(
        edition=OpenLibraryEdition(title="Dune", number_of_pages=412)
    )

    details = OpenLibraryGateway(client=client).fetch(isbn=ISBN)

    assert details == BookDetails(title="Dune", page_count=412)
    assert client.asked == [ISBN.value]


@pytest.mark.unit
def test_unknown_edition_is_none():
    gateway = OpenLibraryGateway(client=StubClient(edition=None))

    assert gateway.fetch(isbn=ISBN) is None
