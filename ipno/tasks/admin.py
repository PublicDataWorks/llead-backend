from django.contrib import admin
from django.contrib.admin import ModelAdmin

from tasks.models import Task, TaskLog


class TaskAdmin(ModelAdmin):
    list_display = ('id', 'task_name', 'task_type', 'should_run')
    readonly_fields = ('command',)

    def has_add_permission(self, request, obj=None):
        return False  # pragma: no cover

    def has_delete_permission(self, request, obj=None):
        return False  # pragma: no cover


class TaskLogAdmin(ModelAdmin):
    list_display = ('task_name', 'created_at', 'error_message', 'finished_at')

    def task_name(self, obj):
        return obj.task.task_name  # pragma: no cover

    def has_add_permission(self, request, obj=None):
        return False  # pragma: no cover

    def has_change_permission(self, request, obj=None):
        return False  # pragma: no cover

    def has_delete_permission(self, request, obj=None):
        return False  # pragma: no cover


admin.site.register(Task, TaskAdmin)
admin.site.register(TaskLog, TaskLogAdmin)
