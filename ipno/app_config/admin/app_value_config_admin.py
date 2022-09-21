from django.contrib import admin
from app_config.models import AppValueConfig


class AppValueConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'description')
    fields = (
        'name', 'value', 'description'
    )
    readonly_fields = ['name', 'description']

    def has_delete_permission(self, request, obj=None):  # pragma: no cover
        return False

    def has_add_permission(self, request, obj=None):  # pragma: no cover
        return False


admin.site.register(AppValueConfig, AppValueConfigAdmin)
