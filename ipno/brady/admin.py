from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Brady


class BradyAdmin(ModelAdmin):
    list_display = ("id", "brady_uid", "created_at", "updated_at")
    search_fields = (
        "brady_uid",
        "uid",
    )


admin.site.register(Brady, BradyAdmin)
