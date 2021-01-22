from django.contrib import admin
from django.contrib.admin import ModelAdmin

from officers.models import Officer


class OfficerAdmin(ModelAdmin):
    list_display = ('id', 'uid', 'last_name', 'first_name', 'created_at', 'updated_at')


admin.site.register(Officer, OfficerAdmin)
