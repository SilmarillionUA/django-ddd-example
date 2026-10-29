from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.translation import gettext, gettext_lazy as _
from django.views.generic import TemplateView, View

from corelib.http import is_htmx
from lending.domain.exceptions import (
    CopyAlreadyOnLoan,
    CopyNotLendable,
    LendingError,
    LoanLimitReached,
    LoanOverdue,
    MembershipRequired,
    MemberSuspended,
    OverdueLoansOutstanding,
    RenewalLimitReached,
    UnknownCopy,
    UnknownLoan,
)
from lending.infrastructure.di import LendingContainer

INCLUDE_RETURNED_PARAM = "returned"
# The tick box sends this when it is on, and nothing when it is off.
INCLUDE_RETURNED_ON = "1"
BARCODE_FIELD = "barcode"
LOAN_TABLE_TEMPLATE = "lending/partials/_loan_table.html"

LENDING_ERROR_MESSAGES = {
    MembershipRequired: _("You need a library card to borrow books."),
    MemberSuspended: _("Your library card is suspended."),
    OverdueLoansOutstanding: _("Return your overdue books first."),
    LoanLimitReached: _("You have as many books out as a card allows."),
    UnknownCopy: _("No copy has this barcode."),
    CopyNotLendable: _("This copy cannot be borrowed."),
    CopyAlreadyOnLoan: _("This copy is already on loan."),
    UnknownLoan: _("This loan is not open on your card."),
    LoanOverdue: _("An overdue book cannot be renewed."),
    RenewalLimitReached: _("This loan has no renewals left."),
}


def my_loans_report(*, request):
    """The report the page, the table and every action response share."""
    return LendingContainer.get_list_my_loans_use_case().execute(
        user=request.user,
        today=timezone.localdate(),
        include_returned=(
            request.GET.get(INCLUDE_RETURNED_PARAM) == INCLUDE_RETURNED_ON
        ),
    )


class MyLoansMixin(LoginRequiredMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["include_returned_param"] = INCLUDE_RETURNED_PARAM
        context["include_returned_on"] = INCLUDE_RETURNED_ON
        context["barcode_field"] = BARCODE_FIELD
        context["my_loans"] = my_loans_report(request=self.request)
        return context


class MyLoansView(MyLoansMixin, TemplateView):
    template_name = "lending/my_loans.html"


class MyLoansTableView(MyLoansMixin, TemplateView):
    http_method_names = ["get"]
    template_name = LOAN_TABLE_TEMPLATE


class LoanActionView(LoginRequiredMixin, View):
    """
    Runs one lending action and answers with the fresh loan table.

    A domain error becomes a message for the member. Anything else is a
    bug and is left to raise. HTMX gets the table fragment back, a
    plain form post gets a redirect to the page.
    """

    http_method_names = ["post"]

    def perform(self, **kwargs) -> str:
        raise NotImplementedError

    def post(self, request, **kwargs):
        try:
            success_message = self.perform(**kwargs)
        except LendingError as exc:
            messages.error(request, LENDING_ERROR_MESSAGES[type(exc)])
        else:
            messages.success(request, success_message)

        if not is_htmx(request):
            return redirect("lending:my_loans")

        return render(
            request,
            LOAN_TABLE_TEMPLATE,
            # The full page shows messages in its layout. The fragment has
            # to carry them itself, or the member never sees the answer.
            {
                "my_loans": my_loans_report(request=request),
                "show_messages": True,
            },
        )


class BorrowCopyView(LoanActionView):
    def perform(self, **kwargs) -> str:
        LendingContainer.get_borrow_copy_use_case().execute(
            user=self.request.user,
            barcode=self.request.POST.get(BARCODE_FIELD, ""),
            today=timezone.localdate(),
        )

        return gettext("Enjoy the book.")


class ReturnLoanView(LoanActionView):
    def perform(self, *, loan_id: int, **kwargs) -> str:
        receipt = LendingContainer.get_return_copy_use_case().execute(
            user=self.request.user,
            loan_id=loan_id,
            today=timezone.localdate(),
        )
        if receipt.late_fee.is_charged:
            return gettext("Book returned. Late fee: %(amount)s.") % {
                "amount": receipt.late_fee.amount
            }

        return gettext("Book returned.")


class RenewLoanView(LoanActionView):
    def perform(self, *, loan_id: int, **kwargs) -> str:
        LendingContainer.get_renew_loan_use_case().execute(
            user=self.request.user,
            loan_id=loan_id,
            today=timezone.localdate(),
        )

        return gettext("Loan renewed.")
