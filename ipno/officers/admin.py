from django.contrib import admin
from django.contrib.admin import ModelAdmin

from officers.models import Officer, Event


class OfficerAdmin(ModelAdmin):
    list_display = ('id', 'uid', 'last_name', 'first_name', 'created_at', 'updated_at')


class EventAdmin(ModelAdmin):
    list_display = (
        'id', 'officer', 'department', 'kind',
        'year', 'month', 'day', 'time', 'raw_date'
    )


admin.site.register(Officer, OfficerAdmin)
admin.site.register(Event, EventAdmin)
