from django.contrib import admin
from django.contrib.admin import ModelAdmin

from documents.models import Document


class DocumentAdmin(ModelAdmin):
    list_display = ('id', 'title', 'created_at', 'updated_at')
    search_fields = ('title',)
    raw_id_fields = ('officers', 'departments')


admin.site.register(Document, DocumentAdmin)
