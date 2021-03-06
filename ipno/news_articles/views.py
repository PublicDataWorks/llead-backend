from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from news_articles.models import NewsArticle
from shared.serializers import NewsArticleSerializer
from news_articles.constants import NEWS_ARTICLES_LIMIT


class NewsArticlesViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(settings.VIEW_CACHING_TIME))
    @cache_control(no_store=True)
    def list(self, request):
        news_articles = NewsArticle.objects.select_related('source').filter(
            matched_sentences__officers__isnull=False
        ).order_by(
            '-published_date',
        ).distinct()[:NEWS_ARTICLES_LIMIT]

        serializer = NewsArticleSerializer(news_articles, many=True)
        return Response(serializer.data)
