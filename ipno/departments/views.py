from django.shortcuts import get_object_or_404
from django.db.models import Count

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from departments.models import Department
from shared.serializers import DepartmentSerializer
from departments.serializers import DepartmentDetailsSerializer
from departments.constants import DEPARTMENTS_LIMIT


class DepartmentsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk):
        queryset = Department.objects.all()
        department = get_object_or_404(queryset, id=pk)
        serializer = DepartmentDetailsSerializer(department)

        return Response(serializer.data)

    def list(self, request):
        departments = Department.objects.all().annotate(
            officersCount=Count('officers__id')
        ).order_by('-officersCount')[:DEPARTMENTS_LIMIT]
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data)
