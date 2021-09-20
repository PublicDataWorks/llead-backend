from django.apps import AppConfig
from django.db import connection

from news_articles.constants import APP_NEWS_ARTICLE_NAMES


class NewsArticleConfig(AppConfig):
    name = 'news_articles'

    def ready(self):
        self.on_app_ready() # noqa

    def on_app_ready(self):
        if "news_articles_newsarticlesource" in connection.introspection.table_names():
            from news_articles.models import NewsArticleSource
            all_news_article_sources = NewsArticleSource.objects.all().values_list('source_name', flat=True)

            for app_news_article_source in APP_NEWS_ARTICLE_NAMES:
                news_article_source_name = app_news_article_source['source_name']
                if news_article_source_name not in all_news_article_sources:
                    NewsArticleSource.objects.create(**app_news_article_source)
