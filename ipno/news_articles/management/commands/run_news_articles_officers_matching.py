from django.core.management import BaseCommand

from news_articles.services import ProcessMatchingArticle, ProcessExcludeArticleOfficer
from utils.search_index import rebuild_search_index


class Command(BaseCommand):
    def handle(self, *args, **options):
        has_news_article = ProcessMatchingArticle().process()
        has_exclude_officer = ProcessExcludeArticleOfficer().process()

        if has_news_article or has_exclude_officer:
            rebuild_search_index()
