from django.contrib import admin
from django.contrib.admin import ModelAdmin

from complaints.models import Complaint


class EventInlineAdmin(admin.TabularInline):
    model = Complaint.events.through
    verbose_name_plural = "Events"
    extra = 0
    raw_id_fields = ("event",)


class ComplaintAdmin(ModelAdmin):
    list_display = ("id", "allegation_uid", "created_at", "updated_at")
    search_fields = (
        "tracking_id",
        "allegation_uid",
    )
    raw_id_fields = ("officers", "departments")
    exclude = ("events",)
    inlines = [EventInlineAdmin]


admin.site.register(Complaint, ComplaintAdmin)
