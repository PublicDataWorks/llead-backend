from django.contrib import admin
from django.contrib.admin import ModelAdmin

from findings.models import Finding


class FindingAdmin(ModelAdmin):
    list_display = ("id", "title", "description")


admin.site.register(Finding, FindingAdmin)
