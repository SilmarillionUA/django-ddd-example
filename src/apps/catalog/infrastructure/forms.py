from django import forms
from django.utils.translation import gettext_lazy as _

from catalog.domain.settings import MAX_COPIES_PER_BOOK_REQUEST

ISBN_INPUT_MAX_LENGTH = 20


class AddBookForm(forms.Form):
    """
    Checks the shape of the input only.

    Whether the ISBN is valid or already taken is a catalog rule, so
    the use case decides it and the view puts its answer on the form.
    """

    isbn = forms.CharField(
        label=_("ISBN"),
        max_length=ISBN_INPUT_MAX_LENGTH,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    title = forms.CharField(
        label=_("Title"),
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    author = forms.CharField(
        label=_("Author"),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    copy_count = forms.IntegerField(
        label=_("Copies"),
        min_value=1,
        max_value=MAX_COPIES_PER_BOOK_REQUEST,
        initial=1,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
