from django.contrib import admin
from django.contrib.admin import ModelAdmin

from departments.models import Department, WrglFile
from news_articles.models import MatchedSentence, NewsArticle


class DepartmentAdmin(ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    filter_horizontal = ('starred_officers', 'starred_news_articles', 'starred_documents', )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "starred_officers":
            kwargs["queryset"] = request.officers
        elif db_field.name == "starred_news_articles":
            matched_sentences = MatchedSentence.objects.filter(
                officers__in=request.officers
            ).all()
            kwargs["queryset"] = NewsArticle.objects.filter(matched_sentences__in=matched_sentences).distinct()
        elif db_field.name == "starred_documents":
            kwargs["queryset"] = request._obj_.documents.order_by('id').distinct().all()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        officers = obj.officers.order_by('id').distinct().all()

        request.officers = officers
        return super(DepartmentAdmin, self).get_form(request, obj, **kwargs)


class WrglFileAdmin(ModelAdmin):
    list_display = ('id', 'slug', 'created_at', 'updated_at')


admin.site.register(Department, DepartmentAdmin)
admin.site.register(WrglFile, WrglFileAdmin)
