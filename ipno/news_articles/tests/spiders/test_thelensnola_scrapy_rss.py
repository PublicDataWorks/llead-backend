from collections import defaultdict
from datetime import datetime
from os.path import dirname, join

from django.test import TestCase
from unittest.mock import patch, MagicMock, Mock, call

from scrapy.http import XmlResponse, Request

from news_articles.models import NewsArticle, CrawledPost
from news_articles.spiders.thelensnola_scrapy_rss import TheLensNolaScrapyRssSpider
from officers.factories import OfficerFactory
from utils.constants import FILE_TYPES


class TheLensNolaScrapyRssSpiderTestCase(TestCase):
    @patch('news_articles.spiders.base_scrapy_rss.GoogleCloudService')
    def setUp(self, mock_gcloud_service):
        self.spider = TheLensNolaScrapyRssSpider()

    def test_parse_item_path(self):
        with open(join(dirname(__file__), 'files', 'thelensnola.xml'), 'r') as f:
            file_content = f.read()
        feed_url = 'https://thelensnola.org/feed/'
        test_feed_response = XmlResponse(
            url=feed_url, request=Request(url=feed_url), body=str.encode(file_content)
        )

        self.articles = self.spider.parse_item(test_feed_response)

        assert len(self.articles) == 3

        assert self.articles[0]['title'] == 'Behind The Lens episode 140: ‘Ready to host’'

        assert self.articles[0]['link'] == 'https://thelensnola.org/2021/08/20/behind-the-lens-episode-140-ready-to' \
                                           '-host/'

        assert self.articles[0]['guid'] == 'https://thelensnola.org/?p=566338'

        assert self.articles[0]['published_date'] == 'Fri, 20 Aug 2021 19:08:47 +0000'

    @patch('news_articles.spiders.thelensnola_scrapy_rss.ItemLoader')
    @patch('news_articles.spiders.thelensnola_scrapy_rss.RSSItem')
    def test_call_parse_items_call_params(self, mock_rss_item, mock_item_loader):
        mock_rss_item_instance = Mock()
        mock_rss_item.return_value = mock_rss_item_instance

        mock_response = Mock()
        mock_xpath = Mock()
        mock_xpath.return_value = ['item1']
        mock_response.xpath = mock_xpath

        mock_item_loader_instance = MagicMock()
        mock_item_loader.return_value = mock_item_loader_instance

        self.spider.parse_item(mock_response)

        mock_response.xpath.assert_called_with("//channel/item")

        mock_item_loader.assert_called_with(
            item=mock_rss_item_instance,
            selector='item1',
        )

        add_xpath_calls_expected = [
            call('title', './title/text()'),
            call('description', './description/p/text()'),
            call('link', './link/text()'),
            call('guid', './guid/text()'),
            call('published_date', './pubDate/text()'),
            call('author', './creator/text()'),
        ]

        mock_item_loader_instance.add_xpath.assert_has_calls(add_xpath_calls_expected)
        mock_item_loader_instance.load_item.assert_called()

    @patch('news_articles.spiders.thelensnola_scrapy_rss.ArticlePdfCreator')
    def test_parse_article(self, mock_article_pdf_creator):
        officer = OfficerFactory()

        mock_adc_instance = MagicMock()
        mocked_pdf_built = 'pdf-buffer'
        mock_adc_instance.build_pdf.return_value = mocked_pdf_built
        mock_article_pdf_creator.return_value = mock_adc_instance

        mocked_content_paragraphs = ['content paragraphs']
        mock_get_all = Mock(return_value=mocked_content_paragraphs)
        mock_css_instance = Mock(getall=mock_get_all)
        mock_css = Mock(return_value=mock_css_instance)
        response = Mock(
            css=mock_css
        )
        published_date = datetime.now().date()
        response.meta = {
            'title': 'response title',
            'link': 'response link',
            'guid': 'response guid',
            'author': 'response author',
            'published_date': published_date,
        }

        mock_parse_paragraphs = Mock()
        mocked_paragraphs = [
            {
                'style': 'Heading1',
                'content': 'header content',
            },
            {
                'style': 'BodyText',
                'content': 'body content',
            }
        ]
        mock_parse_paragraphs.return_value = mocked_paragraphs
        self.spider.parse_paragraphs = mock_parse_paragraphs

        def mock_contains_keyword_side_effect(content):
            return 'body' in content
        mock_contains_keyword = Mock(
            side_effect=mock_contains_keyword_side_effect
        )
        self.spider.contains_keyword = mock_contains_keyword

        mocked_pdf_location = 'pdf_location.pdf'
        mock_get_upload_pdf_location = Mock(
            return_value=mocked_pdf_location
        )
        self.spider.get_upload_pdf_location = mock_get_upload_pdf_location

        mock_upload_file_to_gcloud = Mock(
            return_value='pdf_url.pdf'
        )
        self.spider.upload_file_to_gcloud = mock_upload_file_to_gcloud

        mock_generate_preview_image = Mock(
            return_value='pdf_url-preview.jpg'
        )
        self.spider.generate_preview_image = mock_generate_preview_image
        officers_data = defaultdict(list)
        officers_data[officer.name].append(officer.id)

        self.spider.officers = officers_data
        self.spider.nlp.process = Mock(return_value=[officer.id])

        self.spider.parse_article(response)

        mock_css.assert_called_with("article .entry-content>:not(aside):not(nav)")
        mock_get_all.assert_called()

        mock_parse_paragraphs.assert_called_with(mocked_content_paragraphs)
        mock_contains_keyword.assert_called_with('header content body content')

        mock_article_pdf_creator.assert_called_with(
            title='response title',
            author='response author',
            date=published_date,
            content=mocked_paragraphs,
            link='response link',
        )

        mock_get_upload_pdf_location.assert_called_with(published_date, 'response guid')

        mock_upload_file_to_gcloud.assert_called_with(mocked_pdf_built, mocked_pdf_location, FILE_TYPES['PDF'])
        mock_generate_preview_image.assert_called_with(mocked_pdf_built, 'pdf_location-preview.jpg')

        self.spider.nlp.process.assert_called_with('header content body content', officers_data)

        new_article = NewsArticle.objects.first()
        assert new_article.name == 'thelensnola'
        assert new_article.link == 'response link'
        assert new_article.title == 'response title'
        assert new_article.content == 'header content body content'
        assert new_article.guid == 'response guid'
        assert new_article.author == 'response author'
        assert new_article.published_date == published_date
        assert new_article.url == 'pdf_url.pdf'
        assert new_article.preview_image_url == 'pdf_url-preview.jpg'

        count_news_article = NewsArticle.objects.count()
        assert count_news_article == 1

        crawled_article = NewsArticle.objects.first()
        assert crawled_article.officers.count() == 1

        crawled_post = CrawledPost.objects.first()
        assert crawled_post.name == 'thelensnola'
        assert crawled_post.post_guid == 'response guid'

        count_crawled_post = CrawledPost.objects.count()
        assert count_crawled_post == 1

    def test_parse_article_not_matching_keywords(self):
        mocked_content_paragraphs = ['content paragraphs']
        mock_get_all = Mock(return_value=mocked_content_paragraphs)
        mock_css_instance = Mock(getall=mock_get_all)
        mock_css = Mock(return_value=mock_css_instance)
        response = Mock(
            css=mock_css
        )
        published_date = datetime.now().date()
        response.meta = {
            'title': 'response title',
            'link': 'response link',
            'guid': 'response guid',
            'author': 'response author',
            'published_date': published_date,
        }

        mock_parse_paragraphs = Mock()
        mocked_paragraphs = [
            {
                'style': 'Heading1',
                'content': 'header content',
            },
            {
                'style': 'BodyText',
                'content': 'body content',
            }
        ]
        mock_parse_paragraphs.return_value = mocked_paragraphs
        self.spider.parse_paragraphs = mock_parse_paragraphs

        def mock_contains_keyword_side_effect(content):
            return 'test' in content

        mock_contains_keyword = Mock()
        mock_contains_keyword.side_effect = mock_contains_keyword_side_effect
        self.spider.contains_keyword = mock_contains_keyword

        self.spider.parse_article(response)

        mock_css.assert_called_with("article .entry-content>:not(aside):not(nav)")
        mock_get_all.assert_called()

        mock_parse_paragraphs.assert_called_with(mocked_content_paragraphs)
        mock_contains_keyword.assert_called_with('header content body content')

        count_news_article = NewsArticle.objects.count()
        assert count_news_article == 0

        crawled_post = CrawledPost.objects.first()
        assert crawled_post.name == 'thelensnola'
        assert crawled_post.post_guid == 'response guid'

        count_crawled_post = CrawledPost.objects.count()
        assert count_crawled_post == 1

    @patch('news_articles.spiders.thelensnola_scrapy_rss.ArticlePdfCreator')
    def test_parse_article_not_uploading_file(self, mock_article_pdf_creator):
        mock_adc_instance = MagicMock()
        mocked_pdf_built = 'pdf-buffer'
        mock_adc_instance.build_pdf.return_value = mocked_pdf_built
        mock_article_pdf_creator.return_value = mock_adc_instance

        mocked_content_paragraphs = ['content paragraphs']
        mock_get_all = Mock(return_value=mocked_content_paragraphs)
        mock_css_instance = Mock(getall=mock_get_all)
        mock_css = Mock(return_value=mock_css_instance)
        response = Mock(
            css=mock_css
        )
        published_date = datetime.now().date()
        response.meta = {
            'title': 'response title',
            'link': 'response link',
            'guid': 'response guid',
            'author': 'response author',
            'published_date': published_date,
        }

        mock_parse_paragraphs = Mock()
        mocked_paragraphs = [
            {
                'style': 'Heading1',
                'content': 'header content',
            },
            {
                'style': 'BodyText',
                'content': 'body content',
            }
        ]
        mock_parse_paragraphs.return_value = mocked_paragraphs
        self.spider.parse_paragraphs = mock_parse_paragraphs

        def mock_contains_keyword_side_effect(content):
            return 'body' in content

        mock_contains_keyword = Mock(
            side_effect=mock_contains_keyword_side_effect
        )
        self.spider.contains_keyword = mock_contains_keyword

        mocked_pdf_location = 'pdf_location.pdf'
        mock_get_upload_pdf_location = Mock(
            return_value=mocked_pdf_location
        )
        self.spider.get_upload_pdf_location = mock_get_upload_pdf_location

        mock_upload_file_to_gcloud = Mock(
            return_value=''
        )
        self.spider.upload_file_to_gcloud = mock_upload_file_to_gcloud

        mock_generate_preview_image = Mock(
            return_value=''
        )
        self.spider.generate_preview_image = mock_generate_preview_image

        self.spider.parse_article(response)

        mock_css.assert_called_with("article .entry-content>:not(aside):not(nav)")
        mock_get_all.assert_called()

        mock_parse_paragraphs.assert_called_with(mocked_content_paragraphs)
        mock_contains_keyword.assert_called_with('header content body content')

        mock_article_pdf_creator.assert_called_with(
            title='response title',
            author='response author',
            date=published_date,
            content=mocked_paragraphs,
            link='response link',
        )

        mock_get_upload_pdf_location.assert_called_with(published_date, 'response guid')

        mock_upload_file_to_gcloud.assert_called_with(mocked_pdf_built, mocked_pdf_location, FILE_TYPES['PDF'])
        mock_generate_preview_image.assert_called_with(mocked_pdf_built, 'pdf_location-preview.jpg')

        count_news_article = NewsArticle.objects.count()
        assert count_news_article == 0

        count_crawled_post = CrawledPost.objects.count()
        assert count_crawled_post == 0
