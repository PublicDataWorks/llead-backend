from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from news_articles.models import NewsArticle
from shared.serializers import NewsArticleSerializer
from news_articles.constants import NEWS_ARTICLES_LIMIT


class NewsArticlesViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        news_articles = NewsArticle.objects.filter(
            officers__isnull=False
        ).order_by(
            '-published_date',
        )[:NEWS_ARTICLES_LIMIT]

        serializer = NewsArticleSerializer(news_articles, many=True)
        return Response(serializer.data)
