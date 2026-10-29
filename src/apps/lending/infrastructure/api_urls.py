from django.urls import path

from lending.infrastructure.api import MyLoansApiView

app_name = "lending_api"

urlpatterns = [
    path("loans/", MyLoansApiView.as_view(), name="my_loans"),
]
