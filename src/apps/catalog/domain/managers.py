from typing import TYPE_CHECKING, Optional

from django.db import models
from django.db.models import Count, Q

from catalog.domain.choices import CopyCondition
from catalog.domain.settings import COPY_NUMBER_DIGITS

if TYPE_CHECKING:
    from catalog.domain.models import Book


class CopyQuerySet(models.QuerySet):
    def lendable(self) -> "CopyQuerySet":
        return self.filter(CopyRepository.lendable_condition())


class CopyRepository(models.Manager):
    def get_queryset(self) -> CopyQuerySet:
        return CopyQuerySet(self.model, using=self._db)

    @staticmethod
    def lendable_condition(*, prefix: str = "") -> Q:
        """
        The one place that says which copies may go out on loan.

        A withdrawn copy is gone from the shelf and a damaged one waits
        for repair. `prefix` lets a query on books count the same
        copies through the relation.
        """
        return Q(**{f"{prefix}is_withdrawn": False}) & ~Q(
            **{f"{prefix}condition": CopyCondition.DAMAGED}
        )

    def id_for_barcode(self, *, barcode: str) -> int | None:
        return (
            self.get_queryset()
            .filter(barcode=barcode)
            .values_list("id", flat=True)
            .first()
        )

    def is_lendable(self, *, copy_id: int) -> bool:
        return self.get_queryset().lendable().filter(id=copy_id).exists()

    def add_copies(self, *, book: "Book", count: int) -> None:
        """
        Put `count` new copies of a book on the shelf.

        Numbers continue from the copies the book already has, so a
        barcode never repeats inside one book.
        """
        first_number = self.get_queryset().filter(book=book).count() + 1

        self.bulk_create(
            self.model(
                book=book,
                barcode=self._barcode(isbn=book.isbn, number=number),
            )
            for number in range(first_number, first_number + count)
        )

    @staticmethod
    def _barcode(*, isbn: str, number: int) -> str:
        return f"{isbn}-{number:0{COPY_NUMBER_DIGITS}d}"


class BookQuerySet(models.QuerySet):
    def matching(self, term: str) -> "BookQuerySet":
        return self.filter(
            Q(title__icontains=term)
            | Q(author__icontains=term)
            | Q(isbn__icontains=term)
        )

    def with_lendable_copy_count(self) -> "BookQuerySet":
        return self.annotate(
            lendable_copies=Count(
                "copies",
                filter=CopyRepository.lendable_condition(prefix="copies__"),
            )
        )


class BookRepository(models.Manager):
    def get_queryset(self) -> BookQuerySet:
        return BookQuerySet(self.model, using=self._db)

    def find(self, *, book_id: int) -> Optional["Book"]:
        return self.get_queryset().filter(id=book_id).first()

    def exists_with_isbn(self, *, isbn: str) -> bool:
        return self.get_queryset().filter(isbn=isbn).exists()

    def search_rows(self, *, term: str, limit: int) -> BookQuerySet:
        """
        One page of books with how many copies can go out right now.

        Rows carry plain keys, so the caller never depends on the
        join path to copies.
        """
        books_qs = self.get_queryset()
        if term:
            books_qs = books_qs.matching(term)

        return (
            books_qs.with_lendable_copy_count()
            .values("id", "isbn", "title", "author", "lendable_copies")
            .order_by("title", "id")[:limit]
        )

    def update_details(
        self, *, book_id: int, title: str, page_count: int | None
    ) -> bool:
        updated = (
            self.get_queryset()
            .filter(id=book_id)
            .update(title=title, page_count=page_count)
        )

        return updated > 0
