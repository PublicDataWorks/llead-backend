from django.contrib import admin
from django.contrib.admin import ModelAdmin

from officers.models import Officer, Event


class OfficerAdmin(ModelAdmin):
    list_display = ('id', 'uid', 'last_name', 'first_name', 'created_at', 'updated_at')
    search_fields = ('id', 'uid', 'last_name', 'first_name')


class EventAdmin(ModelAdmin):
    list_display = (
        'id', 'officer', 'department', 'kind',
        'year', 'month', 'day', 'time', 'raw_date'
    )
    raw_id_fields = ('officer', )


admin.site.register(Officer, OfficerAdmin)
admin.site.register(Event, EventAdmin)
