from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import UseOfForce, UseOfForceCitizen, UseOfForceOfficer


class UseOfForceAdmin(ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at')
    search_fields = ('uof_uid', )
    raw_id_fields = ('department',)


class UseOfForceOfficerAdmin(ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at')
    search_fields = ('uof_uid', )
    raw_id_fields = ('officer', 'use_of_force')


class UseOfForceCitizenAdmin(ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at')
    search_fields = ('uof_uid', 'uof_citizen_uid', )


admin.site.register(UseOfForce, UseOfForceAdmin)
admin.site.register(UseOfForceOfficer, UseOfForceOfficerAdmin)
admin.site.register(UseOfForceCitizen, UseOfForceCitizenAdmin)
