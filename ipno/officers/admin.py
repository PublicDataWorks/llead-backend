from django.contrib import admin
from django.contrib.admin import ModelAdmin

from officers.models import Officer, OfficerHistory


class OfficerAdmin(ModelAdmin):
    list_display = ('id', 'uid', 'last_name', 'first_name', 'created_at', 'updated_at')


class OfficerHistoryAdmin(ModelAdmin):
    list_display = ('id', 'officer', 'department', 'badge_no', 'rank_code', 'start_date', 'end_date')


admin.site.register(Officer, OfficerAdmin)
admin.site.register(OfficerHistory, OfficerHistoryAdmin)
