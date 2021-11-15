from django.core.management import call_command
from django.test import TestCase

from news_articles.constants import APP_NEWS_ARTICLE_NAMES
from news_articles.factories import NewsArticleSourceFactory
from news_articles.models import NewsArticleSource


class CreateInitialNewsArticlesSourceTestCase(TestCase):
    def test_call_command(self):
        call_command('create_initial_news_articles_sources')
        sources = NewsArticleSource.objects.all()

        assert sources.count() == len(APP_NEWS_ARTICLE_NAMES)

        for source_data in APP_NEWS_ARTICLE_NAMES:
            source_object = sources.filter(source_name=source_data['source_name']).first()
            assert source_object
            assert source_object.source_name == source_data['source_name']
            assert source_object.source_display_name == source_data['source_display_name']

    def test_call_command_with_partial_created_data(self):
        create_source = APP_NEWS_ARTICLE_NAMES[0]
        NewsArticleSourceFactory(
            source_name=create_source['source_name'],
            source_display_name=create_source['source_display_name']
        )
        assert NewsArticleSource.objects.all().count() == 1

        call_command('create_initial_news_articles_sources')
        sources = NewsArticleSource.objects.all()

        assert sources.count() == len(APP_NEWS_ARTICLE_NAMES)

        for source_data in APP_NEWS_ARTICLE_NAMES:
            source_object = sources.filter(source_name=source_data['source_name']).first()
            assert source_object
            assert source_object.source_name == source_data['source_name']
            assert source_object.source_display_name == source_data['source_display_name']
