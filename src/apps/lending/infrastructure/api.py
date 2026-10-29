from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lending.domain.exceptions import LendingError
from lending.infrastructure.di import LendingContainer
from lending.infrastructure.serializers import (
    BorrowRequestSerializer,
    LoanRowSerializer,
)

ERROR_KEY = "error"


class MyLoansApiView(APIView):
    """
    GET lists the member's open loans. POST borrows a copy by barcode.

    Domain errors come back as 400 with the error's stable `code`, so a
    client can switch on it without parsing text.
    """

    def get(self, request):
        report = LendingContainer.get_list_my_loans_use_case().execute(
            user=request.user, today=timezone.localdate()
        )

        return Response(
            {
                "is_member": report.is_member,
                "loans": LoanRowSerializer(report.rows, many=True).data,
            }
        )

    def post(self, request):
        request_serializer = BorrowRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        try:
            loan_obj = LendingContainer.get_borrow_copy_use_case().execute(
                user=request.user,
                barcode=request_serializer.validated_data.get("barcode"),
                today=timezone.localdate(),
            )
        except LendingError as exc:
            return Response(
                {ERROR_KEY: exc.code}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"id": loan_obj.pk, "due_on": loan_obj.due_on.isoformat()},
            status=status.HTTP_201_CREATED,
        )
