from django.contrib import admin
from django.contrib.admin import ModelAdmin

from departments.models import Department, WrglFile


class DepartmentAdmin(ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')


class WrglFileAdmin(ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')


admin.site.register(Department, DepartmentAdmin)
admin.site.register(WrglFile, WrglFileAdmin)
