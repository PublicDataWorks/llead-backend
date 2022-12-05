from django.contrib import admin
from django.db import models

from adminsortable2.admin import SortableAdminMixin
from martor.widgets import AdminMartorWidget

from app_config.models import FrontPageCard


class FrontPageCardAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("order", "short_content")
    readonly_fields = ("order",)
    formfield_overrides = {
        models.TextField: {"widget": AdminMartorWidget},
    }

    def short_content(self, obj):
        return obj.content[:100]


admin.site.register(FrontPageCard, FrontPageCardAdmin)
