from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, TemplateView

from catalog.domain.exceptions import (
    CopyCountOutOfRange,
    DuplicateIsbn,
    InvalidIsbn,
)
from catalog.infrastructure.di import CatalogContainer
from catalog.infrastructure.forms import AddBookForm
from catalog.infrastructure.tasks import refresh_book_details

BOOK_SEARCH_PARAM = "q"

# Which form field a catalog error belongs to, and what to tell the
# librarian about it.
ADD_BOOK_ERRORS = {
    InvalidIsbn: ("isbn", _("This is not an ISBN.")),
    DuplicateIsbn: ("isbn", _("A book with this ISBN is already listed.")),
    CopyCountOutOfRange: ("copy_count", _("Too many copies at once.")),
}


class BookSearchMixin:
    """The page and the HTMX table read the same search the same way."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["search_param"] = BOOK_SEARCH_PARAM
        context[
            "book_search"
        ] = CatalogContainer.get_search_books_use_case().execute(
            search=self.request.GET.get(BOOK_SEARCH_PARAM, "")
        )
        return context


class BookListView(BookSearchMixin, TemplateView):
    template_name = "catalog/book_list.html"


class BookTableView(BookSearchMixin, TemplateView):
    """The results table on its own, swapped in as the reader types."""

    http_method_names = ["get"]
    template_name = "catalog/partials/_book_table.html"


class BookCreateView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = "catalog/book_form.html"
    form_class = AddBookForm
    success_url = reverse_lazy("catalog:book_list")

    def test_func(self) -> bool:
        return self.request.user.is_staff

    def form_valid(self, form):
        cleaned_data = form.cleaned_data

        try:
            book_obj = CatalogContainer.get_add_book_use_case().execute(
                raw_isbn=cleaned_data.get("isbn"),
                title=cleaned_data.get("title"),
                author=cleaned_data.get("author"),
                copy_count=cleaned_data.get("copy_count"),
            )
        except tuple(ADD_BOOK_ERRORS) as exc:
            field_name, message = ADD_BOOK_ERRORS[type(exc)]
            form.add_error(field_name, message)
            return self.form_invalid(form)

        # Queue the lookup only once the book is in the database, or the
        # worker may run before the row is there to read.
        transaction.on_commit(
            lambda: refresh_book_details.delay(book_id=book_obj.pk)
        )
        messages.success(self.request, _("Book added."))
        return super().form_valid(form)
