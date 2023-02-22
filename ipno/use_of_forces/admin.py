from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import UseOfForce


class UseOfForceAdmin(ModelAdmin):
    list_display = ("id", "created_at", "updated_at")
    search_fields = ("uof_uid",)
    raw_id_fields = ("department",)


admin.site.register(UseOfForce, UseOfForceAdmin)
