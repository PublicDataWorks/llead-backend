from django.contrib import admin

from news_articles.models import NewsArticle, CrawledPost

admin.site.register(NewsArticle)
admin.site.register(CrawledPost)
