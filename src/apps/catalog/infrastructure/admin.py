from django.contrib import admin

from unfold.admin import ModelAdmin, TabularInline

from catalog.domain.models import Book, Copy


class CopyInline(TabularInline):
    model = Copy
    fields = ["barcode", "condition", "is_withdrawn"]
    extra = 0


@admin.register(Book)
class BookAdmin(ModelAdmin):
    list_display = ["title", "author", "isbn", "page_count", "created_at"]
    search_fields = ["title", "author", "isbn"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [CopyInline]


@admin.register(Copy)
class CopyAdmin(ModelAdmin):
    list_display = ["barcode", "book", "condition", "is_withdrawn"]
    list_filter = ["condition", "is_withdrawn"]
    list_select_related = ["book"]
    search_fields = ["barcode", "book__title", "book__isbn"]
    raw_id_fields = ["book"]
    readonly_fields = ["created_at", "updated_at"]
