from django.contrib import admin
from django.contrib.admin import ModelAdmin

from news_articles.models import (
    CrawledPost,
    CrawlerError,
    CrawlerLog,
    MatchingKeyword,
    NewsArticle,
    NewsArticleSource,
    ExcludeOfficer,
    MatchedSentence,
)


class NewsArticleOfficersFilter(admin.SimpleListFilter):
    title = 'Officers'
    parameter_name = 'officers'

    def lookups(self, request, model_admin):
        return (
            ('exist', 'Has officers'),
            ('exclude', 'Has excluded officers'),
            ('not_exist', 'Does not have any officers'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'exist':
            return queryset.filter(matched_sentences__officers__isnull=False).distinct()
        if self.value() == 'exclude':
            return queryset.filter(matched_sentences__excluded_officers__isnull=False).distinct()
        if self.value() == 'not_exist':
            return queryset.filter(matched_sentences__officers__isnull=True).distinct()


class MatchedSentenceInlineAdmin(admin.TabularInline):
    model = MatchedSentence
    fields = ('text', 'extracted_keywords', 'officers')
    show_change_link = True
    can_delete = False
    extra = 0
    list_display = ('text', 'extracted_keywords')

    def has_add_permission(self, request, obj=None):
        return False  # pragma: no cover

    def has_change_permission(self, request, obj=None):
        return False  # pragma: no cover


class NewsArticleAdmin(ModelAdmin):
    list_filter = (NewsArticleOfficersFilter, )
    list_display = ('id', 'source', 'author', 'title')
    inlines = [MatchedSentenceInlineAdmin]


class MatchedArticleOfficersFilter(admin.SimpleListFilter):
    title = 'Officers'
    parameter_name = 'officers'

    def lookups(self, request, model_admin):
        return (
            ('exist', 'Has officers'),
            ('exclude', 'Has excluded officers'),
            ('not_exist', 'Does not have any officers'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'exist':
            return queryset.filter(officers__isnull=False).distinct()
        if self.value() == 'exclude':
            return queryset.filter(excluded_officers__isnull=False).distinct()
        if self.value() == 'not_exist':
            return queryset.filter(officers__isnull=True).distinct()


class MatchedSentenceAdmin(ModelAdmin):
    list_filter = (MatchedArticleOfficersFilter,)
    list_display = ('id', 'article', 'extracted_keywords')
    filter_horizontal = ('officers', 'excluded_officers')


class CrawledPostAdmin(ModelAdmin):
    list_display = ('source', 'post_guid')


class CrawlerErrorInlineAdmin(admin.TabularInline):
    model = CrawlerError
    fields = ('error_message',)
    show_change_link = True
    can_delete = False
    list_display = ('response_url', 'response_status_code', 'error_message')


class CrawlerLogAdmin(ModelAdmin):
    inlines = [CrawlerErrorInlineAdmin]
    list_display = ('source', 'status', 'created_at', 'created_rows', 'error_rows', 'updated_at')

    def has_add_permission(self, request, obj=None):
        return False  # pragma: no cover

    def has_change_permission(self, request, obj=None):
        return False  # pragma: no cover

    def has_delete_permission(self, request, obj=None):
        return False  # pragma: no cover


class CrawlerErrorAdmin(ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False  # pragma: no cover

    def has_change_permission(self, request, obj=None):
        return False  # pragma: no cover

    def has_delete_permission(self, request, obj=None):
        return False  # pragma: no cover


class NewsArticleSourceAdmin(ModelAdmin):
    list_display = ('source_name', 'custom_matching_name')
    readonly_fields = ('source_name', )

    def has_add_permission(self, request, obj=None):
        return False  # pragma: no cover

    def has_delete_permission(self, request, obj=None):
        return False  # pragma: no cover


class MatchingKeywordAdmin(ModelAdmin):
    list_display = ('keywords', 'ran_at', 'status')
    readonly_fields = ('ran_at', )

    def status(self, obj):
        if obj == MatchingKeyword.objects.last():
            return 'Up-to-date'
        else:
            return 'Out-of-date'

    def has_change_permission(self, request, obj=None):
        return False  # pragma: no cover

    def has_delete_permission(self, request, obj=None):
        return False  # pragma: no cover


class ExcludeOfficerAdmin(ModelAdmin):
    list_display = ('officers_list', 'ran_at', 'status')
    readonly_fields = ('ran_at', )
    filter_horizontal = ('officers',)

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        last_exclude_officers = ExcludeOfficer.objects.filter(ran_at__isnull=False).order_by('-created_at').first()
        form.base_fields['officers'].initial = last_exclude_officers.officers.all() if last_exclude_officers else []
        return form

    def status(self, obj):
        if obj == ExcludeOfficer.objects.last():
            return 'Up-to-date'
        else:
            return 'Out-of-date'

    def officers_list(self, obj):
        officers_list = ', '.join([officer.name for officer in obj.officers.all()])
        return f'{officers_list[:100]}{"..." if len(officers_list) > 100 else ""}'

    def has_change_permission(self, request, obj=None):  # pragma: no cover
        return False

    def has_delete_permission(self, request, obj=None):
        return False  # pragma: no cover


admin.site.register(NewsArticle, NewsArticleAdmin)
admin.site.register(MatchedSentence, MatchedSentenceAdmin)
admin.site.register(CrawledPost, CrawledPostAdmin)
admin.site.register(CrawlerLog, CrawlerLogAdmin)
admin.site.register(CrawlerError, CrawlerErrorAdmin)
admin.site.register(NewsArticleSource, NewsArticleSourceAdmin)
admin.site.register(MatchingKeyword, MatchingKeywordAdmin)
admin.site.register(ExcludeOfficer, ExcludeOfficerAdmin)
