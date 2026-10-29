from lending.application.use_cases.borrow_copy import BorrowCopyUseCase
from lending.application.use_cases.list_my_loans import ListMyLoans
from lending.application.use_cases.renew_loan import RenewLoanUseCase
from lending.application.use_cases.return_copy import ReturnCopyUseCase
from lending.application.use_cases.send_due_reminders import (
    SendDueReminders,
)
from lending.domain.services.late_fees import LateFeeCalculator
from lending.infrastructure.gateways import (
    CatalogGateway,
    EmailReminderSender,
)


class LendingContainer:
    @staticmethod
    def get_borrow_copy_use_case() -> BorrowCopyUseCase:
        return BorrowCopyUseCase(catalog=CatalogGateway())

    @staticmethod
    def get_return_copy_use_case() -> ReturnCopyUseCase:
        return ReturnCopyUseCase(late_fees=LateFeeCalculator())

    @staticmethod
    def get_renew_loan_use_case() -> RenewLoanUseCase:
        return RenewLoanUseCase()

    @staticmethod
    def get_list_my_loans_use_case() -> ListMyLoans:
        return ListMyLoans()

    @staticmethod
    def get_send_due_reminders_use_case() -> SendDueReminders:
        return SendDueReminders(reminder_sender=EmailReminderSender())
