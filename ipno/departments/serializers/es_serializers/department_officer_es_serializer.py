from django.db.models import Count

from departments.serializers.department_officers_serializer import (
    DepartmentOfficerSerializer,
)
from officers.models import Officer
from shared.serializers.es_serializers import BaseESSerializer


class DepartmentOfficersESSerializer(BaseESSerializer):
    serializer = DepartmentOfficerSerializer
    model_klass = Officer

    def get_queryset(self, ids):
        return (
            self.model_klass.objects.prefetch_events()
            .filter(
                id__in=ids,
            )
            .annotate(use_of_forces_count=Count("use_of_forces"))
        )
