from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from catalog.domain.choices import CopyCondition
from catalog.domain.managers import BookRepository, CopyRepository
from catalog.domain.settings import BARCODE_MAX_LENGTH
from catalog.domain.types import ISBN_13_LENGTH


class Book(models.Model):
    """
    One title the library holds, known by its ISBN.

    The ISBN is stored cleaned, without dashes or spaces, so a duplicate
    check never trips over how somebody typed it.
    """

    isbn = models.CharField(_("ISBN"), max_length=ISBN_13_LENGTH, unique=True)
    title = models.CharField(_("Title"), max_length=255)
    author = models.CharField(_("Author"), max_length=255, blank=True)
    page_count = models.PositiveIntegerField(
        _("Page count"), null=True, blank=True
    )

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    objects = models.Manager()
    repository = BookRepository()

    class Meta:
        ordering = ["title"]
        verbose_name = _("Book")
        verbose_name_plural = _("Books")

    def __str__(self) -> str:
        return self.title

    def get_admin_url(self) -> str:
        return reverse("admin:catalog_book_change", args=[self.pk])


class Copy(models.Model):
    """
    One physical copy of a book, known by the barcode on its spine.

    Copies are withdrawn instead of deleted, because loans in the
    lending app point at them and keep their history.
    """

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="copies",
        verbose_name=_("Book"),
    )
    barcode = models.CharField(
        _("Barcode"), max_length=BARCODE_MAX_LENGTH, unique=True
    )
    condition = models.CharField(
        _("Condition"),
        max_length=20,
        choices=CopyCondition.choices,
        default=CopyCondition.GOOD,
    )
    is_withdrawn = models.BooleanField(_("Withdrawn"), default=False)

    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    objects = models.Manager()
    repository = CopyRepository()

    class Meta:
        ordering = ["barcode"]
        verbose_name = _("Copy")
        verbose_name_plural = _("Copies")

    def __str__(self) -> str:
        return self.barcode

    def get_admin_url(self) -> str:
        return reverse("admin:catalog_copy_change", args=[self.pk])
