from django.contrib import admin

from schemas.models import Schema, SchemaColumn, Dataset


@admin.register(Schema)
class SchemaAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "created_at", "updated_at")
    search_fields = ("name",)


@admin.register(SchemaColumn)
class SchemaColumnAdmin(admin.ModelAdmin):
    list_display = ("schema", "name", "type", "order", "params")
    search_fields = ("name",)


@admin.register(Dataset)
class Dataset(admin.ModelAdmin):
    list_display = (
        "schema",
        "user",
        "created_at",
        "row_count"
    )
    readonly_fields = ("file", "status", "error_message")