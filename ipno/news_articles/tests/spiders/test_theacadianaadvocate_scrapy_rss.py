from datetime import datetime
from os.path import dirname, join
from unittest.mock import MagicMock, Mock, call, patch

from django.test import TestCase

from scrapy.http import Request, XmlResponse

from news_articles.constants import THEACADIANAADVOCATE_SOURCE
from news_articles.factories import NewsArticleSourceFactory
from news_articles.models import CrawledPost, NewsArticle
from news_articles.spiders import TheAcadianaAdvocateScrapyRssSpider
from utils.constants import FILE_TYPES


class TheAcadianaAdvocateScrapyRssSpiderTestCase(TestCase):
    @patch("news_articles.spiders.base_scrapy_rss.GoogleCloudService")
    def setUp(self, mock_gcloud_service):
        NewsArticleSourceFactory(source_name=THEACADIANAADVOCATE_SOURCE)
        self.spider = TheAcadianaAdvocateScrapyRssSpider()

    def test_parse_item_path(self):
        with open(
            join(dirname(__file__), "files", "theacadianaadvocate.xml"), "r"
        ) as f:
            file_content = f.read()
        feed_url = "https://www.theadvocate.com/search/?f=rss&t=article&c=acadiana&l=100&s=start_time&sd=desc"
        test_feed_response = XmlResponse(
            url=feed_url, request=Request(url=feed_url), body=str.encode(file_content)
        )

        self.articles = self.spider.parse_item(test_feed_response)

        assert len(self.articles) == 2

        assert (
            self.articles[0]["title"]
            == "Erath memorial evokes memories of 8 storm victims, and one man's "
            "promise to honor them"
        )

        assert (
            self.articles[0]["link"]
            == "https://www.theadvocate.com/acadiana/article_a06ad9fa-2e3b-11ec-9f4b"
            "-6714f5d20634.html"
        )

        assert (
            self.articles[0]["guid"].strip()
            == "http://www.theadvocate.com/tncms/asset/editorial/a06ad9fa-2e3b"
            "-11ec-9f4b-6714f5d20634"
        )

        assert self.articles[0]["published_date"] == "Mon, 18 Oct 2021 14:40:00 -0500"

    @patch("news_articles.spiders.theacadianaadvocate_scrapy_rss.ItemLoader")
    @patch("news_articles.spiders.theacadianaadvocate_scrapy_rss.RSSItem")
    def test_call_parse_items_call_params_with_creator(
        self, mock_rss_item, mock_item_loader
    ):
        mock_rss_item_instance = Mock()
        mock_rss_item.return_value = mock_rss_item_instance

        mock_response = Mock()
        mock_xpath = Mock()
        mock_xpath.return_value = ["item1"]
        mock_response.xpath = mock_xpath

        def mock_get_xpath(xpath):
            if xpath == "./creator/text()":
                return ["author"]

        mock_get_xpath = Mock(side_effect=mock_get_xpath)
        mock_item_loader_instance = MagicMock(get_xpath=mock_get_xpath)
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
        ]

        mock_item_loader_instance.add_xpath.assert_has_calls(add_xpath_calls_expected)
        mock_item_loader_instance.add_value.assert_called_with("author", "Author")
        mock_item_loader_instance.load_item.assert_called()

    @patch("news_articles.spiders.theacadianaadvocate_scrapy_rss.ItemLoader")
    @patch("news_articles.spiders.theacadianaadvocate_scrapy_rss.RSSItem")
    def test_call_parse_items_call_params_with_creator_parse_case_sensitive(
        self, mock_rss_item, mock_item_loader
    ):
        mock_rss_item_instance = Mock()
        mock_rss_item.return_value = mock_rss_item_instance

        mock_response = Mock()
        mock_xpath = Mock()
        mock_xpath.return_value = ["item1"]
        mock_response.xpath = mock_xpath

        def mock_get_xpath(xpath):
            if xpath == "./creator/text()":
                return ["BY JEFF ADELSON and JESSICA WILLIAMS | Staff writers"]

        mock_get_xpath = Mock(side_effect=mock_get_xpath)
        mock_item_loader_instance = MagicMock(get_xpath=mock_get_xpath)
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
        ]

        mock_item_loader_instance.add_xpath.assert_has_calls(add_xpath_calls_expected)
        mock_item_loader_instance.add_value.assert_called_with(
            "author", "Jeff Adelson, Jessica Williams"
        )
        mock_item_loader_instance.load_item.assert_called()

    @patch("news_articles.spiders.theacadianaadvocate_scrapy_rss.ItemLoader")
    @patch("news_articles.spiders.theacadianaadvocate_scrapy_rss.RSSItem")
    def test_call_parse_items_call_params_with_author(
        self, mock_rss_item, mock_item_loader
    ):
        mock_rss_item_instance = Mock()
        mock_rss_item.return_value = mock_rss_item_instance

        mock_response = Mock()
        mock_xpath = Mock()
        mock_xpath.return_value = ["item1"]
        mock_response.xpath = mock_xpath

        def mock_get_xpath(xpath):
            if xpath == "./author/text()":
                return ["author@gmail.com (Author)"]

        mock_get_xpath = Mock(side_effect=mock_get_xpath)
        mock_item_loader_instance = MagicMock(get_xpath=mock_get_xpath)
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
        ]

        mock_item_loader_instance.add_xpath.assert_has_calls(add_xpath_calls_expected)
        mock_item_loader_instance.add_value.assert_called_with("author", "Author")
        mock_item_loader_instance.load_item.assert_called()

    @patch("news_articles.spiders.theacadianaadvocate_scrapy_rss.ItemLoader")
    @patch("news_articles.spiders.theacadianaadvocate_scrapy_rss.RSSItem")
    def test_call_parse_items_call_params_without_author(
        self, mock_rss_item, mock_item_loader
    ):
        mock_rss_item_instance = Mock()
        mock_rss_item.return_value = mock_rss_item_instance

        mock_response = Mock()
        mock_xpath = Mock()
        mock_xpath.return_value = ["item1"]
        mock_response.xpath = mock_xpath

        mock_get_xpath = Mock(return_value=None)
        mock_item_loader_instance = MagicMock(get_xpath=mock_get_xpath)
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
        ]

        mock_item_loader_instance.add_xpath.assert_has_calls(add_xpath_calls_expected)
        mock_item_loader_instance.add_value.assert_called_with("author", [""])
        mock_item_loader_instance.load_item.assert_called()

    @patch("news_articles.spiders.theacadianaadvocate_scrapy_rss.ArticlePdfCreator")
    def test_parse_article(self, mock_article_pdf_creator):
        mock_adc_instance = MagicMock()
        mocked_pdf_built = "pdf-buffer"
        mock_adc_instance.build_pdf.return_value = mocked_pdf_built
        mock_article_pdf_creator.return_value = mock_adc_instance

        mocked_content_paragraphs = ["content paragraphs"]
        mock_get_all = Mock(return_value=mocked_content_paragraphs)
        mock_css_instance = Mock(getall=mock_get_all)
        mock_css = Mock(return_value=mock_css_instance)
        response = Mock(css=mock_css)
        published_date = datetime.now().date()
        response.meta = {
            "title": "response title",
            "link": "response link",
            "guid": "response guid",
            "author": "response author",
            "published_date": published_date,
        }

        mock_parse_paragraphs = Mock()
        mocked_paragraphs = [
            {
                "style": "Heading1",
                "content": "header content",
            },
            {
                "style": "BodyText",
                "content": "body content",
            },
        ]
        mock_parse_paragraphs.return_value = mocked_paragraphs
        self.spider.parse_paragraphs = mock_parse_paragraphs

        mocked_pdf_location = "pdf_location.pdf"
        mock_get_upload_pdf_location = Mock(return_value=mocked_pdf_location)
        self.spider.get_upload_pdf_location = mock_get_upload_pdf_location

        mock_upload_file_to_gcloud = Mock(return_value="pdf_url.pdf")
        self.spider.upload_file_to_gcloud = mock_upload_file_to_gcloud

        self.spider.parse_article(response)

        mock_css.assert_called_with('div[itemprop="articleBody"]>:not(meta):not(div)')
        mock_get_all.assert_called()

        mock_parse_paragraphs.assert_called_with(mocked_content_paragraphs)

        mock_article_pdf_creator.assert_called_with(
            title="response title",
            author="response author",
            date=published_date,
            content=mocked_paragraphs,
            link="response link",
        )

        mock_get_upload_pdf_location.assert_called_with(
            published_date, "response title"
        )

        mock_upload_file_to_gcloud.assert_called_with(
            mocked_pdf_built, mocked_pdf_location, FILE_TYPES["PDF"]
        )

        new_article = NewsArticle.objects.first()
        assert new_article.source.source_name == "theacadianaadvocate"
        assert new_article.link == "response link"
        assert new_article.title == "response title"
        assert new_article.content == "header content body content"
        assert new_article.guid == "response guid"
        assert new_article.author == "response author"
        assert new_article.published_date == published_date
        assert new_article.url == "pdf_url.pdf"

        count_news_article = NewsArticle.objects.count()
        assert count_news_article == 1

        crawled_post = CrawledPost.objects.first()
        assert crawled_post.source.source_name == "theacadianaadvocate"
        assert crawled_post.post_guid == "response guid"

        count_crawled_post = CrawledPost.objects.count()
        assert count_crawled_post == 1

    @patch("news_articles.spiders.theacadianaadvocate_scrapy_rss.ArticlePdfCreator")
    def test_parse_article_not_uploading_file(self, mock_article_pdf_creator):
        mock_adc_instance = MagicMock()
        mocked_pdf_built = "pdf-buffer"
        mock_adc_instance.build_pdf.return_value = mocked_pdf_built
        mock_article_pdf_creator.return_value = mock_adc_instance

        mocked_content_paragraphs = ["content paragraphs"]
        mock_get_all = Mock(return_value=mocked_content_paragraphs)
        mock_css_instance = Mock(getall=mock_get_all)
        mock_css = Mock(return_value=mock_css_instance)
        response = Mock(css=mock_css)
        published_date = datetime.now().date()
        response.meta = {
            "title": "response title",
            "link": "response link",
            "guid": "response guid",
            "author": "response author",
            "published_date": published_date,
        }

        mock_parse_paragraphs = Mock()
        mocked_paragraphs = [
            {
                "style": "Heading1",
                "content": "header content",
            },
            {
                "style": "BodyText",
                "content": "body content",
            },
        ]
        mock_parse_paragraphs.return_value = mocked_paragraphs
        self.spider.parse_paragraphs = mock_parse_paragraphs

        mocked_pdf_location = "pdf_location.pdf"
        mock_get_upload_pdf_location = Mock(return_value=mocked_pdf_location)
        self.spider.get_upload_pdf_location = mock_get_upload_pdf_location

        mock_upload_file_to_gcloud = Mock(return_value="")
        self.spider.upload_file_to_gcloud = mock_upload_file_to_gcloud

        self.spider.parse_article(response)

        mock_css.assert_called_with('div[itemprop="articleBody"]>:not(meta):not(div)')
        mock_get_all.assert_called()

        mock_parse_paragraphs.assert_called_with(mocked_content_paragraphs)

        mock_article_pdf_creator.assert_called_with(
            title="response title",
            author="response author",
            date=published_date,
            content=mocked_paragraphs,
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
