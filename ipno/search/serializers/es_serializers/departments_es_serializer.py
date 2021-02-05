from .base_es_serializer import BaseESSerializer
from shared.serializers import DepartmentSerializer
from departments.models import Department


class DepartmentsESSerializer(BaseESSerializer):
    serializer = DepartmentSerializer
    model_klass = Department
