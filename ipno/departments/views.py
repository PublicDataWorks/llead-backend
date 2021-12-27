from itertools import chain

from django.shortcuts import get_object_or_404
from django.db.models import Count, BooleanField, Prefetch
from django.db.models.expressions import F, Value

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination

from departments.models import Department
from departments.serializers import WrglFileSerializer, DepartmentOfficerSerializer, DepartmentNewsArticleSerializer
from news_articles.models import MatchedSentence, NewsArticle
from officers.models import Officer, Event
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
        department = get_object_or_404(queryset, slug=pk)
        serializer = DepartmentDetailsSerializer(department)

        return Response(serializer.data)

    def list(self, request):
        departments = Department.objects.all().annotate(
            officersCount=Count('officers__id', distinct=True)
        ).order_by('-officersCount')[:DEPARTMENTS_LIMIT]
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='documents')
    def documents(self, request, pk):
        department = get_object_or_404(Department, slug=pk)
        q = self.request.query_params.get('q')

        if q:
            search_query = DocumentsSearchQuery(q, department_id=department.id)
            paginator = ESPagination()
            page = paginator.paginate_es_query(search_query, request)
            data = DocumentsESSerializer(page).data
        else:
            queryset = department.documents.prefetch_departments().order_by('-incident_date')
            paginator = LimitOffsetPagination()
            page = paginator.paginate_queryset(queryset, request, view=self)
            data = DocumentWithTextContentSerializer(page, many=True).data

        return paginator.get_paginated_response(data)

    @action(detail=True, methods=['get'], url_path='officers')
    def officers(self, request, pk):
        department = get_object_or_404(Department, slug=pk)

        starred_officers = department.starred_officers.prefetch_related(
            Prefetch(
                'person__officers',
                queryset=Officer.objects.order_by('canonical_person')
            ),
            Prefetch(
                'person__officers__events',
                queryset=Event.objects.order_by(
                    F('year').desc(nulls_last=True),
                    F('month').desc(nulls_last=True),
                    F('day').desc(nulls_last=True),
                )
            ),
        ).annotate(
            is_starred=Value(True, output_field=BooleanField()),
            use_of_forces_count=Count('use_of_forces'),
        ).all()[:DEPARTMENTS_LIMIT]

        starred_officers_count = starred_officers.count()
        sorted_featured_officers = []

        if starred_officers_count < DEPARTMENTS_LIMIT:
            featured_officers = department.officers.filter(
                canonical_person__isnull=False,
            ).exclude(
                id__in=starred_officers,
            )

            sorted_featured_officers = Officer.objects.prefetch_related(
                Prefetch(
                    'person__officers',
                    queryset=Officer.objects.order_by('canonical_person')
                ),
                Prefetch(
                    'person__officers__events',
                    queryset=Event.objects.order_by(
                        F('year').desc(nulls_last=True),
                        F('month').desc(nulls_last=True),
                        F('day').desc(nulls_last=True),
                    )
                ),
            ).filter(
                id__in=featured_officers
            ).annotate(
                is_starred=Value(False, output_field=BooleanField()),
                use_of_forces_count=Count('use_of_forces'),
            ).order_by('-person__all_complaints_count')[:DEPARTMENTS_LIMIT - starred_officers_count]

        officers = list(chain(starred_officers, sorted_featured_officers))

        officers_serializers = DepartmentOfficerSerializer(officers, many=True)

        return Response(officers_serializers.data)

    @action(detail=True, methods=['get'], url_path='news_articles')
    def news_articles(self, request, pk):
        department = get_object_or_404(Department, slug=pk)

        starred_news_articles = department.starred_news_articles.select_related(
            'source'
        ).annotate(
            is_starred=Value(True, output_field=BooleanField())
        ).order_by(
            '-published_date'
        ).all()[:DEPARTMENTS_LIMIT]

        starred_news_articles_count = starred_news_articles.count()
        sorted_featured_news_articles = []

        if starred_news_articles_count < DEPARTMENTS_LIMIT:

            matched_sentences = MatchedSentence.objects.filter(
                officers__in=department.officers.all()
            ).all()

            featured_news_articles = NewsArticle.objects.filter(
                matched_sentences__in=matched_sentences
            ).exclude(
                id__in=starred_news_articles,
            ).distinct()

            sorted_featured_news_articles = NewsArticle.objects.select_related(
                'source'
            ).filter(
                id__in=featured_news_articles
            ).annotate(
                is_starred=Value(False, output_field=BooleanField())
            ).order_by(
                '-published_date'
            )[:DEPARTMENTS_LIMIT - starred_news_articles_count]

        news_articles = list(chain(starred_news_articles, sorted_featured_news_articles))

        news_articles_serializers = DepartmentNewsArticleSerializer(news_articles, many=True)

        return Response(news_articles_serializers.data)

    @action(detail=True, methods=['get'], url_path='datasets')
    def datasets(self, request, pk):
        department = get_object_or_404(Department, slug=pk)
        wrgl_serializers = WrglFileSerializer(department.wrgl_files.order_by('position'), many=True)

        return Response(wrgl_serializers.data)
