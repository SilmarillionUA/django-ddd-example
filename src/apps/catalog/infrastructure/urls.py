from django.urls import path

from catalog.infrastructure.views import (
    BookCreateView,
    BookListView,
    BookTableView,
)

app_name = "catalog"

urlpatterns = [
    path("", BookListView.as_view(), name="book_list"),
    path("table/", BookTableView.as_view(), name="book_table"),
    path("books/new/", BookCreateView.as_view(), name="book_create"),
]
