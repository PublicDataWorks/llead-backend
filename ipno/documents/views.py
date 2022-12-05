from rest_framework import viewsets
from rest_framework.response import Response

from documents.constants import DOCUMENTS_LIMIT
from documents.models import Document
from shared.serializers import DocumentSerializer
from utils.cache_utils import custom_cache


class DocumentsViewSet(viewsets.ViewSet):
    @custom_cache
    def list(self, request):
        documents = (
            Document.objects.prefetch_departments()
            .order_by("docid", "id")
            .distinct("docid")[:DOCUMENTS_LIMIT]
        )

        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)
