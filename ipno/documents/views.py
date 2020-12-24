from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.response import Response

from .models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk):
        queryset = Document.objects.all()
        document = get_object_or_404(queryset, id=pk)
        serializer = DocumentSerializer(document)
        return Response(serializer.data)
