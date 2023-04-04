from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Citizen


class CitizenAdmin(ModelAdmin):
    list_display = ("id", "citizen_uid", "created_at", "updated_at")
    search_fields = ("citizen_uid",)
    raw_id_fields = ("department",)


admin.site.register(Citizen, CitizenAdmin)
