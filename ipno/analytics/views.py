from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from documents.models import Document
from news_articles.models import NewsArticle
from officers.models import Officer
from departments.models import Department


class AnalyticsViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='summary')
    @method_decorator(cache_page(settings.VIEW_CACHING_TIME))
    @cache_control(no_store=True)
    def summary(self, request):
        summary_data = {
            'documents_count': Document.objects.count(),
            'news_articles_count': NewsArticle.objects.count(),
            'officers_count': Officer.objects.filter(canonical_person__isnull=False).count(),
            'departments_count': Department.objects.exclude(
                complaints__isnull=True,
                use_of_forces__isnull=True,
                documents__isnull=True,
            ).count(),
        }

        return Response(summary_data)
