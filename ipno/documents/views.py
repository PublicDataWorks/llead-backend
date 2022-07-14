from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control
from django.conf import settings

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from documents.models import Document
from shared.serializers import DocumentSerializer
from documents.constants import DOCUMENTS_LIMIT


class DocumentsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(settings.VIEW_CACHING_TIME))
    @cache_control(no_store=True)
    def list(self, request):
        documents = Document.objects.prefetch_departments().order_by(
            'docid', 'id'
        ).distinct('docid')[:DOCUMENTS_LIMIT]

        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)
