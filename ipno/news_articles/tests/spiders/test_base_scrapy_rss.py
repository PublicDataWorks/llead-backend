from datetime import datetime
from dateutil.parser import parse

from django.conf import settings
from django.test import TestCase
from scrapy import signals
from scrapy.http import XmlResponse, Request
from unittest.mock import call, patch, Mock, MagicMock

from news_articles.constants import (
    CRAWL_STATUS_ERROR,
    CRAWL_STATUS_FINISHED,
    CRAWL_STATUS_OPENED,
    NEWS_ARTICLE_CLOUD_SPACES,
    TAG_STYLE_MAPPINGS,
)
from news_articles.factories import (
    CrawledPostFactory,
    CrawlerErrorFactory,
    CrawlerLogFactory,
    NewsArticleFactory,
    NewsArticleSourceFactory,
)
from news_articles.models import CrawlerError, CrawlerLog
from news_articles.spiders import ScrapyRssSpider


class ScrapyRssSpiderTestCase(TestCase):
    @patch('news_articles.spiders.base_scrapy_rss.GoogleCloudService')
    def setUp(self, mock_gcloud_service):
        self.source = NewsArticleSourceFactory(source_name='thelens')
        self.spider = ScrapyRssSpider()
        self.spider.name = self.source.source_name
        self.spider.source = self.source

    def test_parse_guid_with_prefix(self):
        self.spider.guid_pre = 'https://thelensnola.org/?p='
        assert self.spider.parse_guid('https://thelensnola.org/?p=566338') == '566338'

    def test_parse_guid_with_postfix(self):
        self.spider.guid_post = ' at https://thelensnola.org'
        assert self.spider.parse_guid('566338 at https://thelensnola.org') == '566338'

    def test_get_crawled_post_guid(self):
        CrawledPostFactory(source=self.source)
        self.spider.name = 'thelens'
        self.spider.get_crawled_post_guid()
        assert self.spider.post_guids

    @patch('scrapy.Request')
    def test_start_request(self, mock_request):
        mock_request_object = Mock()
        mock_request.return_value = mock_request_object
        self.spider.urls = ['http://example.com']
        next(self.spider.start_requests())
        next(self.spider.start_requests())
        mock_request.assert_called_with(url='http://example.com', callback=self.spider.parse_rss)

    @patch('scrapy.Request')
    @patch('news_articles.spiders.ScrapyRssSpider.parse_item')
    def test_parse_rss(self, mock_parse_item, mock_request):
        mock_request_object = Mock()
        mock_request.return_value = mock_request_object
        mock_parse_object = [{
            'title': 'Article Title',
            'description': 'Lorem if sum',
            'link': 'http://example.com',
            'guid': 'GUID-GUID',
            'author': 'Writer',
            'published_date': 'Fri, 20 Aug 2021 19:08:47 +0000',
        }]
        mock_parse_item.return_value = mock_parse_object

        next(self.spider.parse_rss(XmlResponse(
            url='http://example.com',
            request=Request(url='http://example.com'),
            body=str.encode('This is testing content!')
        )))

        date = parse(mock_parse_object[0]['published_date'])

        mock_request.assert_called_with(
            url='http://example.com',
            callback=self.spider.parse_article,
            meta={
                'link': 'http://example.com',
                'guid': 'GUID-GUID',
                'title': 'Article Title',
                'author': 'Writer',
                'published_date': date.date(),
            }
        )

        assert self.spider.post_guids == ['GUID-GUID']

    @patch('scrapy.Request')
    @patch('news_articles.spiders.ScrapyRssSpider.parse_item')
    def test_parse_rss_with_content(self, mock_parse_item, mock_request):
        self.spider.create_article = Mock()

        mock_request_object = Mock()
        mock_request.return_value = mock_request_object
        mock_parse_object = [{
            'title': 'Article Title',
            'description': 'Lorem if sum',
            'link': 'http://example.com',
            'guid': 'GUID-GUID',
            'author': 'Writer',
            'published_date': 'Fri, 20 Aug 2021 19:08:47 +0000',
            'content': 'This is a dummy content.'
        }]
        mock_parse_item.return_value = mock_parse_object

        self.spider.rss_has_content = True
        next(self.spider.parse_rss(XmlResponse(
            url='http://example.com',
            request=Request(url='http://example.com'),
            body=str.encode('This is testing content!')
        )))

        date = parse(mock_parse_object[0]['published_date'])

        expected_article_data = {
            'title': 'Article Title',
            'link': 'http://example.com',
            'guid': 'GUID-GUID',
            'author': 'Writer',
            'published_date': date.date(),
            'content': 'This is a dummy content.'
        }

        self.spider.create_article.assert_called_with(
            expected_article_data
        )

        assert self.spider.post_guids == ['GUID-GUID']

    @patch('scrapy.Request')
    @patch('news_articles.spiders.ScrapyRssSpider.parse_item')
    def test_parse_rss_duplicated_link(self, mock_parse_item, mock_request):
        mock_request_object = Mock()
        mock_request.return_value = mock_request_object
        mock_parse_object = [{
            'title': 'Article Title',
            'description': 'Lorem if sum',
            'link': 'http://example.com',
            'guid': 'GUID-GUID',
            'author': 'Writer',
            'published_date': 'Fri, 20 Aug 2021 19:08:47 +0000',
        }]
        mock_parse_item.return_value = mock_parse_object

        self.spider.post_guids = ['GUID-GUID']

        next(self.spider.parse_rss(XmlResponse(
            url='http://example.com',
            request=Request(url='http://example.com'),
            body=str.encode('This is testing content!')
        )))

        mock_request.assert_not_called

    @patch('news_articles.spiders.base_scrapy_rss.BeautifulSoup')
    def test_parse_section(self, mock_beautiful_soup):
        mock_name = Mock()
        mock_name.name = 'h1'
        mock_current_tag = Mock(return_value=[mock_name])
        mock_get_text = Mock(return_value='Test text')
        mock_beautiful_soup_instance = Mock(
            currentTag=mock_current_tag,
            get_text=mock_get_text
        )
        mock_beautiful_soup.return_value = mock_beautiful_soup_instance

        parsed_section = self.spider.parse_section('<h1></h1>')

        assert parsed_section == {
            'style': TAG_STYLE_MAPPINGS.get('h1'),
            'content': 'Test text'
        }

    @patch('news_articles.spiders.base_scrapy_rss.BeautifulSoup')
    def test_parse_section_with_regex_replace(self, mock_beautiful_soup):
        mock_name = Mock()
        mock_name.name = 'h1'
        mock_current_tag = Mock(return_value=[mock_name])
        mock_get_text = Mock(return_value='Test\xa0\n\n\xa0\n\n text')
        mock_beautiful_soup_instance = Mock(
            currentTag=mock_current_tag,
            get_text=mock_get_text
        )
        mock_beautiful_soup.return_value = mock_beautiful_soup_instance

        parsed_section = self.spider.parse_section('<h1></h1>')

        assert parsed_section == {
            'style': TAG_STYLE_MAPPINGS.get('h1'),
            'content': 'Test\n text'
        }

    @patch('news_articles.spiders.base_scrapy_rss.BeautifulSoup')
    def test_unparse_section(self, mock_beautiful_soup):
        mock_name = Mock()
        mock_name.name = 'aside'
        mock_current_tag = Mock(return_value=[mock_name])
        mock_get_text = Mock(return_value='Test text')
        mock_beautiful_soup_instance = Mock(
            currentTag=mock_current_tag,
            get_text=mock_get_text
        )
        mock_beautiful_soup.return_value = mock_beautiful_soup_instance

        parsed_section = self.spider.parse_section('<aside></aside>')

        assert parsed_section is None

    @patch('news_articles.spiders.base_scrapy_rss.BeautifulSoup')
    def test_parse_invalid_section(self, mock_beautiful_soup):
        mock_name = Mock()
        mock_name.name = 'footer'
        mock_current_tag = Mock(return_value=[mock_name])
        mock_get_text = Mock(return_value='Test text')
        mock_beautiful_soup_instance = Mock(
            currentTag=mock_current_tag,
            get_text=mock_get_text
        )
        mock_beautiful_soup.return_value = mock_beautiful_soup_instance

        parsed_section = self.spider.parse_section('<h1></h1>')

        assert parsed_section == {
            'style': 'BodyText',
            'content': 'Test text'
        }

    def test_parse_paragraphs(self):
        def mock_parse_section_side_effect(paragraph):
            return paragraph
        self.spider.parse_section = MagicMock(side_effect=mock_parse_section_side_effect)

        parsed_paragraphs = self.spider.parse_paragraphs(['paragraph 1', 'paragraph 2', None])

        assert parsed_paragraphs == ['paragraph 1', 'paragraph 2']

    def test_parse_item(self):
        with self.assertRaises(NotImplementedError):
            self.spider.parse_item('response')

    def test_parse_article(self):
        with self.assertRaises(NotImplementedError):
            self.spider.parse_article('response')

    def test_get_upload_pdf_location(self):
        date = datetime.now().date()
        location = self.spider.get_upload_pdf_location(date, 'id')
        file_name = f'{date.strftime("%Y-%m-%d")}_{self.spider.name}_id.pdf'
        assert location == f'{NEWS_ARTICLE_CLOUD_SPACES}/{self.spider.name}/{file_name}'

    def test_upload_file_to_gcloud(self):
        mock_upload_file_from_string = Mock()
        self.spider.gcloud.upload_file_from_string = mock_upload_file_from_string

        result = self.spider.upload_file_to_gcloud('buffer', 'file_location', 'pdf')
        self.spider.gcloud.upload_file_from_string.assert_called_with(
            'file_location',
            'buffer',
            'pdf'
        )
        assert result == f"{settings.GC_PATH}file_location"

    @patch('news_articles.spiders.base_scrapy_rss.logger.error')
    def test_upload_file_to_gcloud_raise_exception(self, mock_logger_error):
        mock_logger_error.return_value = 'error'
        error = ValueError()
        mock_upload_file_from_string = Mock(side_effect=error)
        self.spider.gcloud.upload_file_from_string = mock_upload_file_from_string

        result = self.spider.upload_file_to_gcloud('buffer', 'file_location', 'pdf')
        mock_logger_error.assert_called_with(error)
        assert result is None

    def test_spider_opened(self):
        self.spider.spider_opened(self.spider)

        log = CrawlerLog.objects.first()
        assert log
        assert log.source.source_name == self.spider.name
        assert log.status == CRAWL_STATUS_OPENED

    def test_spider_closed(self):
        log = CrawlerLogFactory(source=self.spider.source, status=CRAWL_STATUS_OPENED)
        CrawlerErrorFactory(log=log)
        NewsArticleFactory(source=self.spider.source)
        self.spider.spider_closed(self.spider, 'reason')

        log = CrawlerLog.objects.first()
        assert log
        assert log.source.source_name == self.spider.name
        assert log.status == CRAWL_STATUS_FINISHED
        assert log.created_rows == 1
        assert log.error_rows == 1

    def test_spider_closed_with_error(self):
        log = CrawlerLogFactory(source=self.spider.source, status=CRAWL_STATUS_ERROR)
        CrawlerErrorFactory(log=log)

        self.spider.spider_closed(self.spider, 'reason')

        log = CrawlerLog.objects.first()
        assert log
        assert log.source.source_name == self.spider.name
        assert log.status == CRAWL_STATUS_ERROR
        assert log.created_rows == 0
        assert log.error_rows == 1

    def test_spider_error(self):
        CrawlerLogFactory(source=self.source, status=CRAWL_STATUS_OPENED)

        response = Mock(url='url', status='status')

        failure = Mock(getTraceback=Mock(return_value='traceback'))

        self.spider.spider_error(failure, response, self.spider)

        log = CrawlerLog.objects.first()
        assert log
        assert log.source.source_name == self.spider.name
        assert log.status == CRAWL_STATUS_ERROR

        error = CrawlerError.objects.first()
        assert error
        assert error.response_url == 'url'
        assert error.response_status_code == 'status'
        assert error.error_message == 'Error occurs while crawling data!\ntraceback'

    @patch('news_articles.spiders.base_scrapy_rss.scrapy.Spider.from_crawler')
    def test_from_crawler(self, mock_from_crawler):
        mock_from_crawler.return_value = self.spider

        mock_connect = Mock()
        crawler = Mock(signals=Mock(connect=mock_connect))

        result = self.spider.from_crawler(crawler)

        expected_calls = [
            call(self.spider.spider_opened, signal=signals.spider_opened),
            call(self.spider.spider_closed, signal=signals.spider_closed),
            call(self.spider.spider_error, signal=signals.spider_error)
        ]

        mock_connect.assert_has_calls(expected_calls)

        assert result == self.spider

    def test_create_article(self):
        with self.assertRaises(NotImplementedError):
            self.spider.create_article('data')
