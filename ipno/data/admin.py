from django.contrib import admin

from data.models import ImportLog


class ImportLogAdmin(admin.ModelAdmin):
    list_display = (
        "data_model",
        "repo_name",
        "commit_hash",
        "status",
        "created_rows",
        "updated_rows",
        "deleted_rows",
        "started_at",
        "finished_at",
    )

    def has_add_permission(self, request, obj=None):
        return False  # pragma: no cover

    def has_change_permission(self, request, obj=None):
        return False  # pragma: no cover

    def has_delete_permission(self, request, obj=None):
        return False  # pragma: no cover


admin.site.register(ImportLog, ImportLogAdmin)
