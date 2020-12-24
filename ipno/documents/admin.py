from django.contrib import admin
from django.contrib.admin import ModelAdmin

from documents.models import Document


class DocumentAdmin(ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')


admin.site.register(Document, DocumentAdmin)
