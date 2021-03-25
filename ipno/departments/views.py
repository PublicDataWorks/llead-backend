from django.shortcuts import get_object_or_404
from django.db.models import Count

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination

from departments.models import Department
from shared.serializers.es_serializers import DocumentsESSerializer
from shared.serializers import DepartmentSerializer, DocumentWithTextContentSerializer
from utils.es_pagination import ESPagination
from departments.serializers import DepartmentDetailsSerializer
from departments.constants import DEPARTMENTS_LIMIT
from departments.queries import DocumentsSearchQuery


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
        q = self.request.query_params.get('q')

        if q:
            search_query = DocumentsSearchQuery(q, department_id=department.id)
            paginator = ESPagination()
            page = paginator.paginate_es_query(search_query, request)
            data = DocumentsESSerializer(page).data
        else:
            queryset = department.documents(prefetch_department=True).order_by('-incident_date')
            paginator = LimitOffsetPagination()
            page = paginator.paginate_queryset(queryset, request, view=self)
            data = DocumentWithTextContentSerializer(page, many=True).data

        return paginator.get_paginated_response(data)
