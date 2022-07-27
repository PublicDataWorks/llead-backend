from django.contrib import admin
from django.contrib.admin import ModelAdmin

from complaints.models import Complaint


class ComplaintAdmin(ModelAdmin):
    list_display = ('id', 'allegation_uid', 'created_at', 'updated_at')
    search_fields = ('tracking_id',)
    raw_id_fields = ('officers', 'departments', 'events')


admin.site.register(Complaint, ComplaintAdmin)
