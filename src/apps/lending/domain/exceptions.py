class LendingError(Exception):
    """
    Base for lending domain errors.

    `code` is stable and machine-readable. The API returns it as is and
    the web views turn it into a message for the member.
    """

    code = "lending_error"


class MembershipRequired(LendingError):
    code = "membership_required"


class MemberSuspended(LendingError):
    code = "member_suspended"


class OverdueLoansOutstanding(LendingError):
    code = "overdue_loans_outstanding"


class LoanLimitReached(LendingError):
    code = "loan_limit_reached"


class UnknownCopy(LendingError):
    code = "unknown_copy"


class CopyNotLendable(LendingError):
    code = "copy_not_lendable"


class CopyAlreadyOnLoan(LendingError):
    code = "copy_already_on_loan"


class UnknownLoan(LendingError):
    code = "unknown_loan"


class LoanOverdue(LendingError):
    code = "loan_overdue"


class RenewalLimitReached(LendingError):
    code = "renewal_limit_reached"
