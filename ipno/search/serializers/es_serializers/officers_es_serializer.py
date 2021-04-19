from shared.serializers.es_serializers import BaseESSerializer
from shared.serializers import OfficerSerializer
from officers.models import Officer


class OfficersESSerializer(BaseESSerializer):
    serializer = OfficerSerializer
    model_klass = Officer

    def get_queryset(self, ids):
        return self.model_klass.objects.prefetch_events().filter(id__in=ids)
