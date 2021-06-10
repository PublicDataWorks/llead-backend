from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from documents.models import Document
from shared.serializers import DocumentSerializer
from documents.constants import DOCUMENTS_LIMIT


class DocumentsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        documents = Document.objects.prefetch_departments().order_by(
            'docid',
        ).distinct('docid')[:DOCUMENTS_LIMIT]

        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)
