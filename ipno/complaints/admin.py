from django.contrib import admin
from django.contrib.admin import ModelAdmin

from complaints.models import Complaint


class ComplaintAdmin(ModelAdmin):
    list_display = ('id', 'allegation_uid', 'created_at', 'updated_at')
    filter_horizontal = ('officers', 'departments')
    raw_id_fields = ('events',)


admin.site.register(Complaint, ComplaintAdmin)
