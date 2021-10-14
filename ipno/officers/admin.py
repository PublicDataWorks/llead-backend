from django.contrib import admin
from django.contrib.admin import ModelAdmin

from news_articles.models import NewsArticle
from officers.models import Officer, Event


class OfficerNewsArticleFilter(admin.SimpleListFilter):
    title = 'News Articles'
    parameter_name = 'news_articles'

    def lookups(self, request, model_admin):
        return (
            ('exist', ('Has news articles')),
            ('not_exist', ('Does not have any news articles')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'exist':
            return queryset.filter(matched_sentences__isnull=False).distinct()
        if self.value() == 'not_exist':
            return queryset.filter(matched_sentences__isnull=True).distinct()


class MatchedSentenceInlineAdmin(admin.TabularInline):
    model = Officer.matched_sentences.through
    verbose_name_plural = 'Sentences'
    extra = 0
    raw_id_fields = ('matchedsentence',)


class ExcludedMatchedSentenceInlineAdmin(admin.TabularInline):
    model = Officer.excluded_matched_sentences.through
    verbose_name_plural = 'Excluded Sentences'
    extra = 0
    raw_id_fields = ('matchedsentence',)


class OfficerAdmin(ModelAdmin):
    list_display = ('id', 'uid', 'last_name', 'first_name', 'count_articles')
    search_fields = ('id', 'uid', 'last_name', 'first_name')
    list_filter = (OfficerNewsArticleFilter,)
    inlines = (MatchedSentenceInlineAdmin, ExcludedMatchedSentenceInlineAdmin,)

    def count_articles(self, obj):
        articles_ids = obj.matched_sentences.all().values_list('article__id', flat=True)  # pragma: no cover
        news_article_timeline_queryset = NewsArticle.objects.prefetch_related('source').filter(
            id__in=articles_ids
        ).distinct()  # pragma: no cover
        return news_article_timeline_queryset.count()  # pragma: no cover


class EventAdmin(ModelAdmin):
    list_display = (
        'id', 'officer', 'department', 'kind',
        'year', 'month', 'day', 'time', 'raw_date'
    )
    raw_id_fields = ('officer', )


admin.site.register(Officer, OfficerAdmin)
admin.site.register(Event, EventAdmin)
