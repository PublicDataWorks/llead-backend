from django.core.management import BaseCommand

from news_articles.services import ProcessMatchingArticle, ProcessExcludeArticleOfficer


class Command(BaseCommand):
    def handle(self, *args, **options):
        ProcessMatchingArticle().process()
        ProcessExcludeArticleOfficer().process()
