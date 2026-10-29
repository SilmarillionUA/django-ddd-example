from rest_framework import serializers

from catalog.domain.settings import BARCODE_MAX_LENGTH


class BorrowRequestSerializer(serializers.Serializer):
    barcode = serializers.CharField(max_length=BARCODE_MAX_LENGTH)


class LoanRowSerializer(serializers.Serializer):
    """
    A `LoanRow` as the API returns it.

    Dates go out as ISO strings and money in cents, so a client never
    has to guess a format or round a float.
    """

    def to_representation(self, instance):
        return {
            "id": instance.loan_id,
            "book_title": instance.book_title,
            "barcode": instance.barcode,
            "borrowed_on": instance.borrowed_on.isoformat(),
            "due_on": instance.due_on.isoformat(),
            "returned_on": (
                instance.returned_on.isoformat()
                if instance.returned_on
                else None
            ),
            "is_overdue": instance.is_overdue,
            "can_renew": instance.can_renew,
            "late_fee_cents": instance.late_fee_cents,
        }
