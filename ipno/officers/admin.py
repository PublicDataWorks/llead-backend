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
    list_display = ('uid', 'last_name', 'first_name', 'sex', 'badges', 'agency', 'aliases')
    search_fields = ('last_name', 'first_name', 'events__badge_no', 'uid')
    list_filter = (OfficerNewsArticleFilter,)
    inlines = (MatchedSentenceInlineAdmin, ExcludedMatchedSentenceInlineAdmin)

    raw_id_fields = ('person', 'department')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('events')

    def badges(self, obj):
        return list(dict.fromkeys([
            event.badge_no for event in obj.events.all()
            if event.badge_no
        ]))


class EventAdmin(ModelAdmin):
    list_display = (
        'id', 'officer', 'department', 'kind',
        'year', 'month', 'day', 'time', 'raw_date'
    )
    raw_id_fields = ('officer', 'department', 'use_of_force', 'appeal')
    list_filter = ('kind', )
    search_fields = ('officer__last_name', 'officer__middle_name', 'officer__first_name', 'event_uid')


admin.site.register(Officer, OfficerAdmin)
admin.site.register(Event, EventAdmin)
