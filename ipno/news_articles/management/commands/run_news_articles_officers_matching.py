from django.core.management import BaseCommand

from news_articles.services.process_matching_article import ProcessMatchingArticle


class Command(BaseCommand):
    def handle(self, *args, **options):
        ProcessMatchingArticle().process()
