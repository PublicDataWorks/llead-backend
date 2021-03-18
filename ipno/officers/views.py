from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from officers.models import Officer, OfficerHistory
from shared.serializers import OfficerSerializer
from officers.serializers import OfficerDetailsSerializer
from officers.constants import OFFICERS_LIMIT


class OfficersViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        officers = Officer.objects.prefetch_related(
            Prefetch(
                'officerhistory_set',
                queryset=OfficerHistory.objects.order_by('-start_date').prefetch_related('department')
            ),
        ).order_by(
            '-created_at'
        )[:OFFICERS_LIMIT]

        serializer = OfficerSerializer(officers, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk):
        officer = get_object_or_404(Officer, id=pk)
        serializer = OfficerDetailsSerializer(officer)

        return Response(serializer.data)
