from django.contrib import admin
from django.contrib.admin import ModelAdmin

from news_articles.models import (
    CrawledPost,
    CrawlerError,
    CrawlerLog,
    NewsArticle,
    NewsArticleSource,
)


class NewsArticleAdmin(ModelAdmin):
    list_display = ('id', 'source', 'author', 'title')
    filter_horizontal = ('officers', )


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


admin.site.register(NewsArticle, NewsArticleAdmin)
admin.site.register(CrawledPost, CrawledPostAdmin)
admin.site.register(CrawlerLog, CrawlerLogAdmin)
admin.site.register(CrawlerError, CrawlerErrorAdmin)
admin.site.register(NewsArticleSource, NewsArticleSourceAdmin)
