from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import UseOfForce, UseOfForceCitizen, UseOfForceOfficer


class UseOfForceAdmin(ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at')


class UseOfForceOfficerAdmin(ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at')


class UseOfForceCitizenAdmin(ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at')


admin.site.register(UseOfForce, UseOfForceAdmin)
admin.site.register(UseOfForceOfficer, UseOfForceOfficerAdmin)
admin.site.register(UseOfForceCitizen, UseOfForceCitizenAdmin)
