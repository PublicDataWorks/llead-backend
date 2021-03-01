from django.contrib import admin
from django.contrib.admin import ModelAdmin

from complaints.models import Complaint


class ComplaintAdmin(ModelAdmin):
    list_display = ('id', 'incident_date', 'tracking_number', 'created_at', 'updated_at')


admin.site.register(Complaint, ComplaintAdmin)
