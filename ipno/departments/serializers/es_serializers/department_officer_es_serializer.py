from django.db.models import Count, Prefetch
from django.db.models.expressions import F

from shared.serializers.es_serializers import BaseESSerializer
from departments.serializers.department_officers_serializer import DepartmentOfficerSerializer
from officers.models import Officer, Event


class DepartmentOfficersESSerializer(BaseESSerializer):
    serializer = DepartmentOfficerSerializer
    model_klass = Officer

    def get_queryset(self, ids):
        return self.model_klass.objects.prefetch_related(
            Prefetch(
                'person__officers__events',
                queryset=Event.objects.order_by(
                    F('year').desc(nulls_last=True),
                    F('month').desc(nulls_last=True),
                    F('day').desc(nulls_last=True),
                )
            )
        ).filter(
            id__in=ids,
        ).annotate(
            use_of_forces_count=Count('use_of_forces')
        )
