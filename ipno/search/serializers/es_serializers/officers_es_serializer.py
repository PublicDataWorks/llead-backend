from officers.models import Officer
from shared.serializers import OfficerSerializer
from shared.serializers.es_serializers import BaseESSerializer


class OfficersESSerializer(BaseESSerializer):
    serializer = OfficerSerializer
    model_klass = Officer

    def get_queryset(self, ids):
        return (
            self.model_klass.objects.prefetch_events()
            .select_related(
                "person__canonical_officer__department",
            )
            .filter(id__in=ids)
        )
