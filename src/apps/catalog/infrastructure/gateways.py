import structlog

from catalog.domain.interfaces import BookDetailsInterface
from catalog.domain.types import BookDetails, Isbn
from corelib.external.open_library import OpenLibraryClient

logger = structlog.get_logger(__name__)


class OpenLibraryGateway(BookDetailsInterface):
    """
    Answers the catalog's question about a book from Open Library.

    The client does the HTTP. This class only turns Open Library's
    edition into the catalog's `BookDetails`. Client errors are left to
    raise, so the Celery task retries them.
    """

    def __init__(self, *, client: OpenLibraryClient) -> None:
        self._client = client

    def fetch(self, *, isbn: Isbn) -> BookDetails | None:
        edition = self._client.edition_by_isbn(isbn=isbn.value)
        if edition is None:
            logger.info("open_library.isbn_not_found", isbn=isbn.value)
            return None

        return BookDetails(
            title=edition.title, page_count=edition.number_of_pages
        )
