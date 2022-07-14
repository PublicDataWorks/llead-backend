from django.contrib import admin

from q_and_a.models import Question


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('section', 'question')


admin.site.register(Question, QuestionAdmin)
