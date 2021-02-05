from django.db.models import Prefetch

from .base_es_serializer import BaseESSerializer
from shared.serializers import OfficerSerializer
from officers.models import Officer, OfficerHistory


class OfficersESSerializer(BaseESSerializer):
    serializer = OfficerSerializer
    model_klass = Officer

    def get_queryset(self, ids):
        return super(OfficersESSerializer, self).get_queryset(ids).prefetch_related(
            Prefetch(
                'officerhistory_set',
                queryset=OfficerHistory.objects.order_by('-start_date').prefetch_related('department')
            ),
        )
