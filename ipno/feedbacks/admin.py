from django.contrib import admin
from django.contrib.admin import ModelAdmin

from feedbacks.models import Feedback


class FeedbackAdmin(ModelAdmin):
    list_display = ('id', 'email', 'message', 'created_at', 'updated_at')


admin.site.register(Feedback, FeedbackAdmin)
