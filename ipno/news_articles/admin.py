from django.contrib import admin
from django.contrib.admin import ModelAdmin

from news_articles.models import NewsArticle, CrawledPost


class NewsArticleAdmin(ModelAdmin):
    list_display = ('id', 'source_name', 'author', 'title')


class CrawledPostAdmin(ModelAdmin):
    list_display = ('source_name', 'post_guid')


admin.site.register(NewsArticle, NewsArticleAdmin)
admin.site.register(CrawledPost, CrawledPostAdmin)
