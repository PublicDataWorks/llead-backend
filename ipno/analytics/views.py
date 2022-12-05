from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from departments.models import Department
from documents.models import Document
from news_articles.models import NewsArticle
from officers.models import Officer
from utils.cache_utils import custom_cache


class AnalyticsViewSet(ViewSet):
    @action(detail=False, methods=["get"], url_path="summary")
    @custom_cache
    def summary(self, request):
        summary_data = {
            "documents_count": Document.objects.count(),
            "news_articles_count": NewsArticle.objects.count(),
            "officers_count": Officer.objects.filter(
                canonical_person__isnull=False
            ).count(),
            "departments_count": Department.objects.count(),
        }

        return Response(summary_data)
