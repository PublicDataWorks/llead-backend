from django.contrib import admin
from django.contrib.admin import ModelAdmin

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
            return queryset.filter(news_articles__isnull=False).distinct()
        if self.value() == 'not_exist':
            return queryset.filter(news_articles__isnull=True).distinct()


class NewsArticleInlineAdmin(admin.TabularInline):
    model = Officer.news_articles.through
    extra = 0


class OfficerAdmin(ModelAdmin):
    list_display = ('id', 'uid', 'last_name', 'first_name', 'count_articles')
    search_fields = ('id', 'uid', 'last_name', 'first_name')
    list_filter = (OfficerNewsArticleFilter,)
    inlines = (NewsArticleInlineAdmin, )

    def count_articles(self, obj):
        return obj.news_articles.count()  # pragma: no cover


class EventAdmin(ModelAdmin):
    list_display = (
        'id', 'officer', 'department', 'kind',
        'year', 'month', 'day', 'time', 'raw_date'
    )
    raw_id_fields = ('officer', )


admin.site.register(Officer, OfficerAdmin)
admin.site.register(Event, EventAdmin)
