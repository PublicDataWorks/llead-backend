from rest_framework import viewsets
from rest_framework.response import Response

from q_and_a.models import Section
from q_and_a.serializers import QAndASerializer
from utils.cache_utils import custom_cache


class QAndAViewSet(viewsets.ViewSet):
    @custom_cache
    def list(self, request):
        sections = Section.objects.prefetch_related('questions').all()

        serializer = QAndASerializer(sections, many=True)
        return Response(serializer.data)
