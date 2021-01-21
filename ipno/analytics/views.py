import datetime
import pytz

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from documents.models import Document
from officers.models import Officer
from departments.models import Department

RECENT_DAYS = 30


class AnalyticsViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        date_n = datetime.datetime.now(pytz.utc) - datetime.timedelta(days=RECENT_DAYS)

        summary_data = {
            'documents_count': Document.objects.count(),
            'officers_count': Officer.objects.count(),
            'departments_count': Department.objects.count(),
            'recent_documents_count': Document.objects.filter(created_at__gt=date_n).count(),
            'recent_officers_count': Officer.objects.filter(created_at__gt=date_n).count(),
            'recent_departments_count': Department.objects.filter(created_at__gt=date_n).count(),
            'recent_days': RECENT_DAYS,
        }

        return Response(summary_data)
