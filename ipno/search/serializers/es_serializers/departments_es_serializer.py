from departments.models import Department
from shared.serializers import DepartmentSerializer
from shared.serializers.es_serializers import BaseESSerializer


class DepartmentsESSerializer(BaseESSerializer):
    serializer = DepartmentSerializer
    model_klass = Department
