from django.contrib import admin

from data.models import WrglRepo, ImportLog


class WrglRepoAdmin(admin.ModelAdmin):
    list_display = ('data_model', 'repo_name', 'commit_hash')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ImportLogAdmin(admin.ModelAdmin):
    list_display = (
        'data_model',
        'repo_name',
        'commit_hash',
        'status',
        'created_rows',
        'updated_rows',
        'deleted_rows',
        'started_at',
        'finished_at',
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(WrglRepo, WrglRepoAdmin)
admin.site.register(ImportLog, ImportLogAdmin)
