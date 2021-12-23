from django.contrib import admin
from django.contrib.admin import ModelAdmin

from departments.models import Department, WrglFile
from officers.models import Officer


class DepartmentAdmin(ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    filter_horizontal = ('starred_officers', )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "starred_officers":
            kwargs["queryset"] = Officer.objects.filter(departments=request._obj_).distinct()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super(DepartmentAdmin, self).get_form(request, obj, **kwargs)


class WrglFileAdmin(ModelAdmin):
    list_display = ('id', 'slug', 'created_at', 'updated_at')


admin.site.register(Department, DepartmentAdmin)
admin.site.register(WrglFile, WrglFileAdmin)
