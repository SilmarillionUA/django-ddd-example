from catalog.application.use_cases.add_book import AddBookUseCase
from catalog.application.use_cases.refresh_book_details import (
    RefreshBookDetailsUseCase,
)
from catalog.application.use_cases.search_books import SearchBooks
from catalog.infrastructure.gateways import OpenLibraryGateway
from corelib.external.open_library import OpenLibraryClient


class CatalogContainer:
    @staticmethod
    def get_add_book_use_case() -> AddBookUseCase:
        return AddBookUseCase()

    @staticmethod
    def get_search_books_use_case() -> SearchBooks:
        return SearchBooks()

    @staticmethod
    def get_refresh_book_details_use_case() -> RefreshBookDetailsUseCase:
        return RefreshBookDetailsUseCase(
            book_details=OpenLibraryGateway(client=OpenLibraryClient())
        )
