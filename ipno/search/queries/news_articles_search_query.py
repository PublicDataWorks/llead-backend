from shared.queries.base_search_query import BaseSearchQuery
from news_articles.documents import NewsArticleESDoc


class NewsArticlesSearchQuery(BaseSearchQuery):
    document_klass = NewsArticleESDoc
    fields = ['title', 'content', 'author', 'source_name']

    def query(self):
        return super(NewsArticlesSearchQuery, self).query(order='-published_date').highlight('content', 'author')
