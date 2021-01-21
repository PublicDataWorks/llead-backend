from django.contrib import admin
from django.contrib.admin import ModelAdmin

from departments.models import Department


class DepartmentAdmin(ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')


admin.site.register(Department, DepartmentAdmin)
