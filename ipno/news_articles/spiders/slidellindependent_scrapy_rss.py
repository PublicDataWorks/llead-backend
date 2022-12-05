import re

from scrapy.loader import ItemLoader

from news_articles.constants import SLIDELLINDEPENDENT_SOURCE
from news_articles.models import CrawledPost, NewsArticle
from news_articles.spiders.base_scrapy_rss import RSSItem, ScrapyRssSpider
from utils.constants import FILE_TYPES
from utils.pdf_creator import ArticlePdfCreator


class SlidellIndependentScrapyRssSpider(ScrapyRssSpider):
    name = SLIDELLINDEPENDENT_SOURCE
    allowed_domains = ["slidell-independent.com"]
    urls = ["https://www.slidell-independent.com/feed/"]
    guid_pre = "https://www.slidell-independent.com/?p="

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

            items.append(loader.load_item())

        return items

    def parse_article(self, response):
        title = response.meta.get("title")
        link = response.meta.get("link")
        guid = response.meta.get("guid")
        author = response.meta.get("author")
        published_date = response.meta.get("published_date")

        raw_parsed_author = response.css(".post-entry>p").get()
        content_paragraphs = response.css(".post-entry>p").getall()

        if raw_parsed_author and raw_parsed_author.startswith("<p>By "):
            parsed_author = re.search(r"<p>By (.*)<br>", raw_parsed_author)
            author = parsed_author.group(1) if parsed_author else author
            content_paragraphs = content_paragraphs[1:]

        paragraphs = self.parse_paragraphs(content_paragraphs)

        save_crawled_post = True

        text_content = " ".join([paragraph["content"] for paragraph in paragraphs])

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
