from shared.queries.base_search_query import BaseSearchQuery
from news_articles.documents import NewsArticleESDoc


class NewsArticlesSearchQuery(BaseSearchQuery):
    document_klass = NewsArticleESDoc
    fields = ['title', 'content', 'author', 'source_name']

    def query(self, order=None, pre_term_query=None):
        return super(NewsArticlesSearchQuery, self).query(
            order='-published_date',
            pre_term_query={
                'is_hidden': False
            }
        ).highlight('content', 'author')
