from django.contrib import admin
from django.contrib.admin import ModelAdmin

from officers.models import Officer
from people.models import Person


class OfficerInlineAdmin(admin.TabularInline):
    model = Officer
    show_change_link = True
    can_delete = False
    fields = ('uid', 'first_name', 'last_name')
    extra = 0

    def has_change_permission(self, request, obj=None):
        return False  # pragma: no cover


class PersonAdmin(ModelAdmin):
    inlines = [OfficerInlineAdmin]
    list_display = ('person_id', 'canonical_officer',)
    raw_id_fields = ('canonical_officer',)


admin.site.register(Person, PersonAdmin)
