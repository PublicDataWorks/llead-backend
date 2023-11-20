import re

from scrapy.loader import ItemLoader

from news_articles.constants import NOLA_SOURCE
from news_articles.models import CrawledPost, NewsArticle
from news_articles.spiders.base_scrapy_rss import RSSItem, ScrapyRssSpider
from utils.constants import FILE_TYPES
from utils.pdf_creator import ArticlePdfCreator


class NolaScrapyRssSpider(ScrapyRssSpider):
    name = NOLA_SOURCE
    allowed_domains = ["nola.com", "www.theadvocate.com"]
    urls = [
        (
            "https://www.theadvocate.com/search/?t=article&l=100&c%5b%5d=baton_rouge/news*,baton_rouge/opinion*,"
            "baton_rouge/sports*,new_orleans/sports/saints&f=rss"
        ),
        (
            "https://www.theadvocate.com/search/?t=article&l=100&c%5b%20%5d=new_orleans/news*,"
            "baton_rouge/news/politics/legislature,baton_rouge/news/politics,new_orleans/opinion*,"
            "baton_rouge/opinion/stephanie_grace,baton_rouge/opinion/jeff_sadow,ba%20ton_rouge/opinion/mark_ballard,"
            "new_orleans/sports*,baton_rouge/sports/lsu&f=rss"
        ),
        (
            "https://www.theadvocate.com/search/?t=article&l=100&c%5b%20%5d=acadiana/"
            "news*,acadiana/entertainment_life*,"
            "acadiana/sports*,baton_rouge/sports/lsu,baton_rouge/news/politics/legislature,baton_rouge/news/politics,"
            "new_orleans/opinion*,bat%20on_rouge/opinion/stephanie_grace,baton_rouge/opinion/jeff_sadow,"
            "baton_rouge/opinion/mark_ballard,new_orleans/sports/saints&f=rss"
        ),
    ]
    guid_pre = "http://www.theadvocate.com/tncms/asset/editorial/"

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

            creator = loader.get_xpath("./creator/text()")
            author = loader.get_xpath("./author/text()")

            if creator:
                by_name = creator[0].split(" | ")[0]
                by_pattern = re.compile("by ", re.IGNORECASE)
                name = by_pattern.sub("", by_name)
                and_pattern = re.compile(" and", re.IGNORECASE)
                name = and_pattern.sub(",", name)
                loader.add_value("author", name.title())
            elif author:
                name = re.search(r"\((.+?)\)", author[0]).group(1)
                loader.add_value("author", name.title())
            else:
                loader.add_value("author", [""])

            items.append(loader.load_item())

        return items

    def parse_article(self, response):
        title = response.meta.get("title")
        link = response.meta.get("link")
        guid = response.meta.get("guid")
        author = response.meta.get("author")
        published_date = response.meta.get("published_date")

        content_paragraphs = response.css('div[itemprop="articleBody"] p').getall()

        paragraphs = self.parse_paragraphs(content_paragraphs)

        save_crawled_post = True

        text_content = " ".join([paragraph["content"] for paragraph in paragraphs])
        text_content = text_content.strip()

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
