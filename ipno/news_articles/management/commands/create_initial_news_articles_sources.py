from django.core.management import BaseCommand

from news_articles.constants import APP_NEWS_ARTICLE_NAMES
from news_articles.models import NewsArticleSource


class Command(BaseCommand):
    def handle(self, *args, **options):
        for source in APP_NEWS_ARTICLE_NAMES:
            source_name = NewsArticleSource.objects.filter(source_name=source['source_name']).first()
            if not source_name:
                NewsArticleSource.objects.create(**source)
