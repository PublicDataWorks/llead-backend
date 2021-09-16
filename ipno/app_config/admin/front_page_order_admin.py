from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from app_config.models import FrontPageOrder


@admin.register(FrontPageOrder)
class MyModelAdmin(SortableAdminMixin, admin.ModelAdmin):
    readonly_fields = ('section', 'order')

    def has_add_permission(self, request, obj=None):
        return False  # pragma: no cover

    def has_delete_permission(self, request, obj=None):
        return False  # pragma: no cover
