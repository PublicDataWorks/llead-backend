from collections import defaultdict
from datetime import datetime
from os.path import dirname, join
from unittest.mock import MagicMock, Mock, call, patch

from django.test import TestCase

from scrapy.http import Request, XmlResponse

from news_articles.constants import BRPROUD_SOURCE
from news_articles.factories import NewsArticleSourceFactory
from news_articles.models import CrawledPost, NewsArticle
from news_articles.spiders import BRProudScrapyRssSpider
from officers.factories import OfficerFactory
from utils.constants import FILE_TYPES


class BRProudScrapyRssSpiderTestCase(TestCase):
    @patch("news_articles.spiders.base_scrapy_rss.GoogleCloudService")
    def setUp(self, mock_gcloud_service):
        NewsArticleSourceFactory(source_name=BRPROUD_SOURCE)
        self.spider = BRProudScrapyRssSpider()

    def test_parse_item_path(self):
        with open(join(dirname(__file__), "files", "brproud.xml"), "r") as f:
            file_content = f.read()
        feed_url = "https://www.brproud.com/feed/"
        test_feed_response = XmlResponse(
            url=feed_url, request=Request(url=feed_url), body=str.encode(file_content)
        )
        test_feed_response.selector.remove_namespaces()

        self.articles = self.spider.parse_item(test_feed_response)

        assert len(self.articles) == 2

        assert (
            self.articles[1]["title"].strip()
            == "East Ascension Drainage meeting becomes heated, board member "
            "walked out by police"
        )

        assert (
            self.articles[1]["link"].strip()
            == "https://www.brproud.com/news/east-ascension-drainage-meeting"
            "-becomes-heated-board-member-walked-out-by-police/"
        )

        assert self.articles[1]["guid"].strip() == "https://www.brproud.com/?p=1094209"

        assert (
            self.articles[1]["published_date"].strip()
            == "Tue, 19 Oct 2021 02:42:30 +0000"
        )

        assert self.articles[1]["author"] == "Michael Scheidt"

        assert self.articles[1]["content"][:20] == '\n<figure class="wp-b'
        assert self.articles[1]["content"][-20:] == "for November 8.</p>\n"

    @patch("news_articles.spiders.brproud_scrapy_rss.ItemLoader")
    @patch("news_articles.spiders.brproud_scrapy_rss.RSSItem")
    def test_call_parse_items_call_params(self, mock_rss_item, mock_item_loader):
        mock_rss_item_instance = Mock()
        mock_rss_item.return_value = mock_rss_item_instance

        mock_response = Mock()
        mock_xpath = Mock()
        mock_xpath.return_value = ["item1"]
        mock_response.xpath = mock_xpath

        mock_item_loader_instance = MagicMock()
        mock_item_loader.return_value = mock_item_loader_instance

        self.spider.parse_item(mock_response)

        mock_response.xpath.assert_called_with("//channel/item")

        mock_item_loader.assert_called_with(
            item=mock_rss_item_instance,
            selector="item1",
        )

        add_xpath_calls_expected = [
            call("title", "./title/text()"),
            call("description", "./description/text()"),
            call("link", "./link/text()"),
            call("guid", "./guid/text()"),
            call("published_date", "./pubDate/text()"),
            call("author", "./creator/text()"),
            call("content", "./encoded/text()"),
        ]

        mock_item_loader_instance.add_xpath.assert_has_calls(add_xpath_calls_expected)
        mock_item_loader_instance.load_item.assert_called()

    @patch("news_articles.spiders.brproud_scrapy_rss.ArticlePdfCreator")
    def test_create_article(self, mock_article_pdf_creator):
        officer = OfficerFactory()

        mock_adc_instance = MagicMock()
        mocked_pdf_built = "pdf-buffer"
        mock_adc_instance.build_pdf.return_value = mocked_pdf_built
        mock_article_pdf_creator.return_value = mock_adc_instance

        published_date = datetime.now().date()
        article_data = {
            "title": "response title",
            "link": "response link",
            "guid": "response guid",
            "author": "response author",
            "published_date": published_date,
            "content": "body content",
        }

        mock_parse_section = Mock()
        mocked_section = {
            "style": "BodyText",
            "content": "body content",
        }

        mock_parse_section.return_value = mocked_section
        self.spider.parse_section = mock_parse_section

        mocked_pdf_location = "pdf_location.pdf"
        mock_get_upload_pdf_location = Mock(return_value=mocked_pdf_location)
        self.spider.get_upload_pdf_location = mock_get_upload_pdf_location

        mock_upload_file_to_gcloud = Mock(return_value="pdf_url.pdf")
        self.spider.upload_file_to_gcloud = mock_upload_file_to_gcloud

        officers_data = defaultdict(list)
        officers_data[officer.name].append(officer.id)

        self.spider.officers = officers_data

        self.spider.create_article(article_data)

        mock_parse_section.assert_called_with("body content")

        mock_article_pdf_creator.assert_called_with(
            title="response title",
            author="response author",
            date=published_date,
            content=[mocked_section],
            link="response link",
        )

        mock_get_upload_pdf_location.assert_called_with(
            published_date, "response title"
        )

        mock_upload_file_to_gcloud.assert_called_with(
            mocked_pdf_built, mocked_pdf_location, FILE_TYPES["PDF"]
        )

        new_article = NewsArticle.objects.first()
        assert new_article.source.source_name == "brproud"
        assert new_article.link == "response link"
        assert new_article.title == "response title"
        assert new_article.content == "body content"
        assert new_article.guid == "response guid"
        assert new_article.author == "response author"
        assert new_article.published_date == published_date
        assert new_article.url == "pdf_url.pdf"

        count_news_article = NewsArticle.objects.count()
        assert count_news_article == 1

        crawled_post = CrawledPost.objects.first()
        assert crawled_post.source.source_name == "brproud"
        assert crawled_post.post_guid == "response guid"

        count_crawled_post = CrawledPost.objects.count()
        assert count_crawled_post == 1

    @patch("news_articles.spiders.brproud_scrapy_rss.ArticlePdfCreator")
    def test_create_article_not_upload_file(self, mock_article_pdf_creator):
        officer = OfficerFactory()

        mock_adc_instance = MagicMock()
        mocked_pdf_built = "pdf-buffer"
        mock_adc_instance.build_pdf.return_value = mocked_pdf_built
        mock_article_pdf_creator.return_value = mock_adc_instance

        published_date = datetime.now().date()
        article_data = {
            "title": "response title",
            "link": "response link",
            "guid": "response guid",
            "author": "response author",
            "published_date": published_date,
            "content": "body content",
        }

        mock_parse_section = Mock()
        mocked_section = {
            "style": "BodyText",
            "content": "body content",
        }

        mock_parse_section.return_value = mocked_section
        self.spider.parse_section = mock_parse_section

        mocked_pdf_location = "pdf_location.pdf"
        mock_get_upload_pdf_location = Mock(return_value=mocked_pdf_location)
        self.spider.get_upload_pdf_location = mock_get_upload_pdf_location

        mock_upload_file_to_gcloud = Mock(return_value="")
        self.spider.upload_file_to_gcloud = mock_upload_file_to_gcloud

        officers_data = defaultdict(list)
        officers_data[officer.name].append(officer.id)

        self.spider.officers = officers_data

        self.spider.create_article(article_data)

        mock_parse_section.assert_called_with("body content")

        mock_article_pdf_creator.assert_called_with(
            title="response title",
            author="response author",
            date=published_date,
            content=[mocked_section],
            link="response link",
        )

        mock_get_upload_pdf_location.assert_called_with(
            published_date, "response title"
        )

        mock_upload_file_to_gcloud.assert_called_with(
            mocked_pdf_built, mocked_pdf_location, FILE_TYPES["PDF"]
        )

        count_news_article = NewsArticle.objects.count()
        assert count_news_article == 0

        count_crawled_post = CrawledPost.objects.count()
        assert count_crawled_post == 0
