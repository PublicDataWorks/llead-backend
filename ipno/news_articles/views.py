from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from app_config.models import AppValueConfig
from news_articles.constants import NEWS_ARTICLES_LIMIT
from news_articles.documents import NewsArticleESDoc
from news_articles.models import NewsArticle
from shared.serializers import NewsArticleSerializer
from utils.cache_utils import flush_news_article_related_caches


class NewsArticlesViewSet(viewsets.ViewSet):
    def list(self, request):
        if not request.user.is_anonymous and request.user.is_admin:
            news_articles = (
                NewsArticle.objects.select_related("source")
                .filter(
                    is_hidden=False,
                )
                .order_by(
                    "-published_date",
                )
                .distinct()[:NEWS_ARTICLES_LIMIT]
            )
        else:
            threshold = float(
                AppValueConfig.objects.get(name="NEWS_ARTICLE_THRESHOLD").value
            )

            news_articles = (
                NewsArticle.objects.select_related("source")
                .prefetch_related("news_article_classifications")
                .filter(
                    Q(is_hidden=False),
                    Q(news_article_classifications__isnull=True)
                    | Q(news_article_classifications__score__gte=threshold),
                )
                .order_by(
                    "-published_date",
                )
                .distinct()[:NEWS_ARTICLES_LIMIT]
            )

        serializer = NewsArticleSerializer(news_articles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def hide(self, request, pk=None):
        queryset = NewsArticle.objects.all()
        news_article = get_object_or_404(queryset, pk=pk)

        news_article.is_hidden = True
        news_article.save()

        es_doc = NewsArticleESDoc.get(id=pk)
        es_doc.update(news_article)

        flush_news_article_related_caches()

        return Response({"detail": "the news articles is hidden"})
