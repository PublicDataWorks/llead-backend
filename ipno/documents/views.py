from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from documents.models import Document
from documents.serializers import DocumentSerializer


class DocumentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk):
        queryset = Document.objects.all()
        document = get_object_or_404(queryset, id=pk)
        serializer = DocumentSerializer(document)
        return Response(serializer.data)
