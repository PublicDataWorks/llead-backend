from django.core.management import BaseCommand
from django.utils import timezone

from news_articles.services import ProcessExcludeArticleOfficer, ProcessMatchingArticle
from utils.cache_utils import flush_news_article_related_caches
from utils.search_index import rebuild_search_index


class Command(BaseCommand):
    def handle(self, *args, **options):
        start_time = timezone.now()
        has_news_article = ProcessMatchingArticle().process()
        has_exclude_officer = ProcessExcludeArticleOfficer().process()

        if has_news_article or has_exclude_officer:
            rebuild_search_index()

        if has_news_article:
            flush_news_article_related_caches(start_time)
