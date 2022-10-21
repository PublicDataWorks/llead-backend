from django.contrib import admin
from django.contrib.admin import ModelAdmin

from appeals.models import Appeal


class AppealAdmin(ModelAdmin):
    list_display = ('id', 'appeal_uid', 'created_at', 'updated_at')
    search_fields = ('id', 'appeal_uid', )
    raw_id_fields = ('officer', 'department', )


admin.site.register(Appeal, AppealAdmin)
