from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import PostOfficerHistory


class PostOfficerHistoryAdmin(ModelAdmin):
    list_display = (
        "uid",
        "history_id",
        "agency",
    )
    search_fields = (
        "uid",
        "history_id",
    )


admin.site.register(PostOfficerHistory, PostOfficerHistoryAdmin)
