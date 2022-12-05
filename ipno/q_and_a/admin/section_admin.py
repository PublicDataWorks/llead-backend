from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin

from q_and_a.models import Question, Section


class QuestionInlineAdmin(admin.StackedInline):
    model = Question
    extra = 0


class SectionAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ("order", "name")
    inlines = (QuestionInlineAdmin,)


admin.site.register(Section, SectionAdmin)
