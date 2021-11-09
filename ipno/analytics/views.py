import datetime
import pytz

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from documents.models import Document
from officers.models import Officer
from departments.models import Department
from app_config.models import AppConfig

DEFAULT_RECENT_DAYS = 30


class AnalyticsViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        recent_date_config = AppConfig.objects.filter(name='ANALYTIC_RECENT_DAYS').first()

        recent_date = int(recent_date_config.value) if recent_date_config else DEFAULT_RECENT_DAYS

        date_n = datetime.datetime.now(pytz.utc) - datetime.timedelta(days=recent_date)

        summary_data = {
            'documents_count': Document.objects.count(),
            'officers_count': Officer.objects.filter(canonical_person__isnull=False).count(),
            'departments_count': Department.objects.count(),
            'recent_documents_count': Document.objects.filter(created_at__gt=date_n).count(),
            'recent_officers_count': Officer.objects.filter(canonical_person__isnull=False, created_at__gt=date_n).count(),
            'recent_departments_count': Department.objects.filter(created_at__gt=date_n).count(),
            'recent_days': recent_date,
        }

        return Response(summary_data)
