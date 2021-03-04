from django.shortcuts import get_object_or_404
from django.db.models import Count

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination

from departments.models import Department
from shared.serializers import DepartmentSerializer
from departments.serializers import DepartmentDetailsSerializer, DocumentSerializer
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

    @action(detail=True, methods=['get'], url_path='documents')
    def documents(self, request, pk):
        department = get_object_or_404(Department, id=pk)
        queryset = department.documents.order_by('-incident_date')
        paginator = LimitOffsetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = DocumentSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
