from django.db import models
from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from martor.widgets import AdminMartorWidget

from app_config.models import FrontPageCard


class FrontPageCardAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('order', 'content')
    readonly_fields = ('order',)
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }


admin.site.register(FrontPageCard, FrontPageCardAdmin)
