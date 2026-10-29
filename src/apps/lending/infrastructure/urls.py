from django.urls import path

from lending.infrastructure.views import (
    BorrowCopyView,
    MyLoansTableView,
    MyLoansView,
    RenewLoanView,
    ReturnLoanView,
)

app_name = "lending"

urlpatterns = [
    path("", MyLoansView.as_view(), name="my_loans"),
    path("table/", MyLoansTableView.as_view(), name="my_loans_table"),
    path("borrow/", BorrowCopyView.as_view(), name="borrow"),
    path(
        "<int:loan_id>/return/", ReturnLoanView.as_view(), name="return_loan"
    ),
    path("<int:loan_id>/renew/", RenewLoanView.as_view(), name="renew_loan"),
]
