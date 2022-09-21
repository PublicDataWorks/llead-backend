from rest_framework import viewsets
from rest_framework.response import Response

from q_and_a.models import Section
from q_and_a.serializers import QAndASerializer


class QAndAViewSet(viewsets.ViewSet):
    def list(self, request):
        sections = Section.objects.prefetch_related('questions').all()

        serializer = QAndASerializer(sections, many=True)
        return Response(serializer.data)
