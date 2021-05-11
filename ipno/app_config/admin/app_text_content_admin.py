from django.db import models
from django.contrib import admin

from martor.widgets import AdminMartorWidget

from app_config.models import AppTextContent


class AppTextContentAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'description')
    fields = (
        'name', 'value', 'description'
    )
    readonly_fields = ['name', 'description']
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }

    def has_delete_permission(self, request, obj=None):  # pragma: no cover
        return False

    def has_add_permission(self, request, obj=None):  # pragma: no cover
        return False


admin.site.register(AppTextContent, AppTextContentAdmin)
