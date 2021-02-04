from django.db.models import Count

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from departments.models import Department
from shared.serializers import DepartmentSerializer
from departments.constants import DEPARTMENTS_LIMIT


class DepartmentsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        departments = Department.objects.all().annotate(
            officersCount=Count('officers__id')
        ).order_by('-officersCount')[:DEPARTMENTS_LIMIT]
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data)
