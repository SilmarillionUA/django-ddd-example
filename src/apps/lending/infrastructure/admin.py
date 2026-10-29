from django.contrib import admin

from unfold.admin import ModelAdmin

from lending.domain.models import Loan, Member


@admin.register(Member)
class MemberAdmin(ModelAdmin):
    list_display = ["user", "is_suspended", "created_at"]
    list_filter = ["is_suspended"]
    list_select_related = ["user"]
    search_fields = ["user__username", "user__email"]
    raw_id_fields = ["user"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Loan)
class LoanAdmin(ModelAdmin):
    list_display = [
        "copy",
        "member",
        "borrowed_on",
        "due_on",
        "returned_on",
        "renewal_count",
        "late_fee_cents",
    ]
    list_filter = ["returned_on", "due_on"]
    list_select_related = ["copy__book", "member__user"]
    search_fields = [
        "copy__barcode",
        "copy__book__title",
        "member__user__username",
    ]
    raw_id_fields = ["member", "copy"]
    # Fees and renewals come from the use cases. Editing them here would
    # skip the rules that produce them.
    readonly_fields = [
        "renewal_count",
        "late_fee_cents",
        "reminder_sent_on",
        "created_at",
        "updated_at",
    ]
