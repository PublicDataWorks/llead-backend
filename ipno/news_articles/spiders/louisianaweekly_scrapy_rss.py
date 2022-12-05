import re

from bs4 import BeautifulSoup
from scrapy.loader import ItemLoader

from news_articles.constants import LOUISIANAWEEKLY_SOURCE
from news_articles.models import CrawledPost, NewsArticle
from news_articles.spiders.base_scrapy_rss import RSSItem, ScrapyRssSpider
from utils.constants import FILE_TYPES
from utils.pdf_creator import ArticlePdfCreator


class LouisianaWeeklyScrapyRssSpider(ScrapyRssSpider):
    name = LOUISIANAWEEKLY_SOURCE
    allowed_domains = ["louisianaweekly.com"]
    urls = ["http://www.louisianaweekly.com/feed/"]
    guid_pre = "http://www.louisianaweekly.com/?p="
    rss_has_content = True

    def __init__(self):
        super().__init__()

    def parse_item(self, response):
        channel_items = response.xpath("//channel/item")
        items = []
        for item in channel_items:
            loader = ItemLoader(item=RSSItem(), selector=item)
            loader.add_xpath("title", "./title/text()")
            loader.add_xpath("description", "./description/text()")
            loader.add_xpath("link", "./link/text()")
            loader.add_xpath("guid", "./guid/text()")
            loader.add_xpath("published_date", "./pubDate/text()")
            loader.add_xpath("author", "./creator/text()")
            loader.add_xpath("content", "./encoded/text()")

            items.append(loader.load_item())

        return items

    def create_article(self, article_data):
        title = article_data.get("title")
        link = article_data.get("link")
        guid = article_data.get("guid")
        author = article_data.get("author")
        published_date = article_data.get("published_date")
        content = article_data.get("content")

        parsed_first_paragraph = BeautifulSoup(content, "html.parser").find("p")
        first_paragraph = (
            parsed_first_paragraph.text if parsed_first_paragraph else None
        )

        paragraphs = [self.parse_section(content)]

        save_crawled_post = True

        text_content = " ".join([paragraph["content"] for paragraph in paragraphs])

        if first_paragraph and first_paragraph.startswith("By "):
            parsed_author = re.search(r"By (.*)\n", first_paragraph)
            author = parsed_author.group(1) if parsed_author else author
            text_content = text_content.replace(first_paragraph, "")
            paragraphs = [
                {"style": paragraphs[0].get("style"), "content": text_content}
            ]

        pdf_buffer = ArticlePdfCreator(
            title=title,
            author=author,
            date=published_date,
            content=paragraphs,
            link=link,
        ).build_pdf()

        pdf_location = self.get_upload_pdf_location(published_date, title)

        uploaded_url = self.upload_file_to_gcloud(
            pdf_buffer, pdf_location, FILE_TYPES["PDF"]
        )

        if uploaded_url:
            news_article_data = NewsArticle(
                source=self.source,
                link=link,
                title=title,
                content=text_content,
                guid=guid,
                author=author,
                published_date=published_date,
                url=uploaded_url,
            )
            news_article_data.save()
        else:
            save_crawled_post = False

        if save_crawled_post:
            crawled_post = CrawledPost(source=self.source, post_guid=guid)
            crawled_post.save()
