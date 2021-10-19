from django.utils import timezone
from unittest.mock import call, Mock, patch

from django.conf import settings
from django.test import TestCase

from data.constants import NEWS_ARTICLE_MODEL_NAME
from data.factories import WrglRepoFactory
from data.models import WrglRepo
from news_articles.constants import NEWS_ARTICLE_WRGL_COLUMNS
from news_articles.factories import CrawledPostFactory, NewsArticleFactory
from news_articles.factories.matched_sentence_factory import MatchedSentenceFactory
from news_articles.management.commands.run_news_articles_crawlers import Command
from news_articles.models import NewsArticle
from news_articles.spiders import (
    TheLensNolaScrapyRssSpider,
    VermillionTodayScrapyRssSpider,
    NolaScrapyRssSpider,
    TtfMagazineScrapyRssSpider,
    KlaxScrapyRssSpider,
    BRProudScrapyRssSpider,
    HeraldGuideScrapyRssSpider,
    BossierPressScrapyRssSpider,
)
from news_articles.spiders import CapitalCityNewsScrapyRssSpider
from officers.factories import OfficerFactory


class CommandTestCase(TestCase):
    def setUp(self):
        self.command = Command()

    @patch('news_articles.management.commands.run_news_articles_crawlers.CrawlerProcess')
    @patch('news_articles.management.commands.run_news_articles_crawlers.get_project_settings')
    def test_handle(self, mock_get_project_settings, mock_crawler_process):
        mock_get_project_settings.return_value = 'settings'
        mock_crawl = Mock()
        mock_start = Mock()
        mock_crawler_process_object = Mock(crawl=mock_crawl, start=mock_start)
        mock_crawler_process.return_value = mock_crawler_process_object
        self.command.commit_data_to_wrgl = Mock()

        self.command.handle()

        mock_get_project_settings.assert_called()
        mock_crawler_process.assert_called_with('settings')
        calls_similarity = [
            call(TheLensNolaScrapyRssSpider),
            call(NolaScrapyRssSpider),
            call(VermillionTodayScrapyRssSpider),
            call(TtfMagazineScrapyRssSpider),
            call(KlaxScrapyRssSpider),
            call(CapitalCityNewsScrapyRssSpider),
            call(BRProudScrapyRssSpider),
            call(HeraldGuideScrapyRssSpider),
            call(BossierPressScrapyRssSpider),
        ]
        mock_crawl.assert_has_calls(calls_similarity)
        mock_start.assert_called()
        self.command.commit_data_to_wrgl.assert_called()

    def test_commit_data_to_wrgl(self):
        date = timezone.now()
        news = NewsArticleFactory()
        officer = OfficerFactory()
        matched_sentence = MatchedSentenceFactory(article=news)
        matched_sentence.officers.add(officer)
        CrawledPostFactory(post_guid=news.guid)

        WrglRepoFactory(
            data_model=NEWS_ARTICLE_MODEL_NAME,
            repo_name=settings.NEWS_ARTICLE_WRGL_REPO,
            commit_hash='old_commit',
        )

        def mock_generate_csv_file_side_effect(data, columns):
            return data

        mock_generate_csv_file = Mock()
        mock_generate_csv_file.side_effect = mock_generate_csv_file_side_effect
        mock_create_wrgl_commit = Mock()

        mock_json = Mock()
        mock_json.return_value = {
            "hash": "hash",
            "contentHash": "contentHash"
        }
        mock_response_object = Mock(json=mock_json)
        mock_create_wrgl_commit.return_value = mock_response_object

        mock_wrgl_generator_object = Mock(
            generate_csv_file=mock_generate_csv_file,
            create_wrgl_commit=mock_create_wrgl_commit
        )
        self.command.wrgl = mock_wrgl_generator_object

        news = NewsArticle.objects.all()

        self.command.wrgl_repos_mapping = [
            {
                'data': news,
                'columns': NEWS_ARTICLE_WRGL_COLUMNS,
                'wrgl_repo': settings.NEWS_ARTICLE_WRGL_REPO,
                'wrgl_model_name': NEWS_ARTICLE_MODEL_NAME,
            },
        ]

        self.command.commit_data_to_wrgl(date)

        mock_generate_csv_file.assert_called_with(news, NEWS_ARTICLE_WRGL_COLUMNS)

        called_create_wrgl_similarity = [
            call(
                settings.NEWS_ARTICLE_WRGL_REPO,
                '+ 1 object(s)',
                'id',
                news
            ),
            call().json(),
        ]

        self.command.wrgl.create_wrgl_commit.assert_has_calls(called_create_wrgl_similarity)

        news_wrgl = WrglRepo.objects.get(data_model=NEWS_ARTICLE_MODEL_NAME)

        assert news_wrgl.commit_hash == 'hash'

    def test_not_updating_commit_hash(self):
        date = timezone.now()
        news = NewsArticleFactory()
        officer = OfficerFactory()
        matched_sentence = MatchedSentenceFactory(article=news)
        matched_sentence.officers.add(officer)
        CrawledPostFactory(post_guid=news.guid)

        WrglRepoFactory(
            data_model=NEWS_ARTICLE_MODEL_NAME,
            repo_name=settings.NEWS_ARTICLE_WRGL_REPO,
            commit_hash='hash',
        )

        def mock_generate_csv_file_side_effect(data, columns):
            return data

        mock_generate_csv_file = Mock()
        mock_generate_csv_file.side_effect = mock_generate_csv_file_side_effect
        mock_create_wrgl_commit = Mock()

        mock_json = Mock()
        mock_json.return_value = {
            "hash": "hash",
            "contentHash": "contentHash"
        }
        mock_response_object = Mock(json=mock_json)
        mock_create_wrgl_commit.return_value = mock_response_object

        mock_wrgl_generator_object = Mock(
            generate_csv_file=mock_generate_csv_file,
            create_wrgl_commit=mock_create_wrgl_commit
        )
        self.command.wrgl = mock_wrgl_generator_object

        news = NewsArticle.objects.all()

        self.command.wrgl_repos_mapping = [
            {
                'data': news,
                'columns': NEWS_ARTICLE_WRGL_COLUMNS,
                'wrgl_repo': settings.NEWS_ARTICLE_WRGL_REPO,
                'wrgl_model_name': NEWS_ARTICLE_MODEL_NAME,
            },
        ]

        self.command.commit_data_to_wrgl(date)

        mock_generate_csv_file.assert_called_with(news, NEWS_ARTICLE_WRGL_COLUMNS)

        called_create_wrgl_similarity = [
            call(
                settings.NEWS_ARTICLE_WRGL_REPO,
                '+ 1 object(s)',
                'id',
                news
            ),
            call().json(),
        ]

        self.command.wrgl.create_wrgl_commit.assert_has_calls(called_create_wrgl_similarity)

        news_wrgl = WrglRepo.objects.get(data_model=NEWS_ARTICLE_MODEL_NAME)

        assert news_wrgl.commit_hash == 'hash'

    def test_not_updating_commit_data_to_wrgl(self):
        date = timezone.now()

        WrglRepoFactory(
            data_model=NEWS_ARTICLE_MODEL_NAME,
            repo_name=settings.NEWS_ARTICLE_WRGL_REPO,
            commit_hash='hash',
        )

        def mock_generate_csv_file_side_effect(data, columns):
            return data

        mock_generate_csv_file = Mock()
        mock_generate_csv_file.side_effect = mock_generate_csv_file_side_effect
        mock_create_wrgl_commit = Mock()

        mock_json = Mock()
        mock_json.return_value = {
            "hash": "hash",
            "contentHash": "contentHash"
        }
        mock_response_object = Mock(json=mock_json)
        mock_create_wrgl_commit.return_value = mock_response_object

        mock_wrgl_generator_object = Mock(
            generate_csv_file=mock_generate_csv_file,
            create_wrgl_commit=mock_create_wrgl_commit
        )
        self.command.wrgl = mock_wrgl_generator_object

        news = NewsArticle.objects.all()

        self.command.wrgl_repos_mapping = [
            {
                'data': news,
                'columns': NEWS_ARTICLE_WRGL_COLUMNS,
                'wrgl_repo': settings.NEWS_ARTICLE_WRGL_REPO,
                'wrgl_model_name': NEWS_ARTICLE_MODEL_NAME,
            },
        ]

        self.command.commit_data_to_wrgl(date)

        mock_generate_csv_file.assert_called_with(news, NEWS_ARTICLE_WRGL_COLUMNS)

        news_wrgl = WrglRepo.objects.get(data_model=NEWS_ARTICLE_MODEL_NAME)

        assert news_wrgl.commit_hash == 'hash'
