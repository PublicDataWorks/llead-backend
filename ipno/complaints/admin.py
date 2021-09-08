from django.contrib import admin
from django.contrib.admin import ModelAdmin

from complaints.models import Complaint


class ComplaintAdmin(ModelAdmin):
    list_display = ('id', 'complaint_uid', 'allegation_uid', 'charge_uid', 'created_at', 'updated_at')
    filter_horizontal = ('officers', 'departments', 'events')


admin.site.register(Complaint, ComplaintAdmin)
