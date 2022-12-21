from itertools import chain

from django.db.models import Count, Prefetch, Q
from django.db.models.expressions import Case, Value, When
from django.db.models.fields import BooleanField
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from departments.constants import DEPARTMENTS_LIMIT
from departments.models import Department, OfficerMovement
from departments.serializers import (
    DepartmentDetailsSerializer,
    DepartmentDocumentSerializer,
    DepartmentNewsArticleSerializer,
    DepartmentOfficerSerializer,
    OfficerMovementSerializer,
    WrglFileSerializer,
)
from departments.serializers.es_serializers import (
    DepartmentDocumentsESSerializer,
    DepartmentNewsArticlesESSerializer,
    DepartmentOfficersESSerializer,
)
from documents.models import Document
from news_articles.models import MatchedSentence, NewsArticle
from officers.models import Officer
from search.queries import (
    DocumentsSearchQuery,
    NewsArticlesSearchQuery,
    OfficersSearchQuery,
)
from shared.serializers import DepartmentSerializer
from utils.cache_utils import custom_cache
from utils.es_pagination import ESPagination


class DepartmentsViewSet(viewsets.ViewSet):
    @custom_cache
    def retrieve(self, request, pk):
        queryset = Department.objects.all()
        department = get_object_or_404(queryset, slug=pk)
        serializer = DepartmentDetailsSerializer(department)

        return Response(serializer.data)

    @custom_cache
    def list(self, request):
        departments = (
            Department.objects.exclude(
                complaints__isnull=True,
                use_of_forces__isnull=True,
                documents__isnull=True,
            )
            .annotate(officersCount=Count("officers__id", distinct=True))
            .order_by("-officersCount")[:DEPARTMENTS_LIMIT]
        )
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="search")
    def search(self, request, pk):
        q = self.request.query_params.get("q", "")
        kind = self.request.query_params.get("kind", "")

        serializer_mapping = {
            "officers": DepartmentOfficersESSerializer,
            "news_articles": DepartmentNewsArticlesESSerializer,
            "documents": DepartmentDocumentsESSerializer,
        }

        search_query_mapping = {
            "officers": OfficersSearchQuery,
            "news_articles": NewsArticlesSearchQuery,
            "documents": DocumentsSearchQuery,
        }

        if kind not in serializer_mapping.keys():
            return Response(
                f"Missing kind param, must be in {serializer_mapping.keys()}",
                status=HTTP_400_BAD_REQUEST,
            )

        search_query = search_query_mapping[kind](q, pk)

        paginator = ESPagination()
        page = paginator.paginate_es_query(search_query, request)

        data = serializer_mapping[kind](page).data

        return paginator.get_paginated_response(data)

    @action(detail=True, methods=["get"], url_path="documents")
    @custom_cache
    def documents(self, request, pk):
        department = get_object_or_404(Department, slug=pk)

        starred_documents = (
            department.starred_documents.prefetch_related()
            .annotate(
                is_starred=Value(True, output_field=BooleanField()),
            )
            .all()[:DEPARTMENTS_LIMIT]
        )

        starred_documents_count = starred_documents.count()
        sorted_featured_documents = []

        if starred_documents_count < DEPARTMENTS_LIMIT:
            featured_documents = department.documents.exclude(
                id__in=starred_documents,
            )

            sorted_featured_documents = (
                Document.objects.filter(id__in=featured_documents)
                .annotate(
                    is_starred=Value(False, output_field=BooleanField()),
                )
                .order_by("-incident_date")[
                    : DEPARTMENTS_LIMIT - starred_documents_count
                ]
            )

        documents = list(chain(starred_documents, sorted_featured_documents))

        documents_serializers = DepartmentDocumentSerializer(documents, many=True)

        return Response(documents_serializers.data)

    @action(detail=True, methods=["get"], url_path="officers")
    @custom_cache
    def officers(self, request, pk):
        department = get_object_or_404(Department, slug=pk)

        other_prefetches = (Prefetch("department"),)

        starred_officers = (
            department.starred_officers.prefetch_events(other_prefetches)
            .annotate(
                is_starred=Value(True, output_field=BooleanField()),
                use_of_forces_count=Count("use_of_forces"),
            )
            .all()[:DEPARTMENTS_LIMIT]
        )

        starred_officers_count = starred_officers.count()
        sorted_featured_officers = []

        if starred_officers_count < DEPARTMENTS_LIMIT:
            featured_officers = department.officers.filter(
                canonical_person__isnull=False,
            ).exclude(
                id__in=starred_officers,
            )

            sorted_featured_officers = (
                Officer.objects.prefetch_events(other_prefetches)
                .filter(id__in=featured_officers)
                .annotate(
                    is_starred=Value(False, output_field=BooleanField()),
                    use_of_forces_count=Count("use_of_forces"),
                )
                .order_by("-person__all_complaints_count")[
                    : DEPARTMENTS_LIMIT - starred_officers_count
                ]
            )

        officers = list(chain(starred_officers, sorted_featured_officers))

        officers_serializers = DepartmentOfficerSerializer(officers, many=True)

        return Response(officers_serializers.data)

    @action(detail=True, methods=["get"], url_path="news_articles")
    @custom_cache
    def news_articles(self, request, pk):
        department = get_object_or_404(Department, slug=pk)

        starred_news_articles = (
            department.starred_news_articles.filter(is_hidden=False)
            .select_related("source")
            .annotate(is_starred=Value(True, output_field=BooleanField()))
            .order_by("-published_date")
            .all()[:DEPARTMENTS_LIMIT]
        )

        starred_news_articles_count = starred_news_articles.count()
        sorted_featured_news_articles = []

        if starred_news_articles_count < DEPARTMENTS_LIMIT:
            matched_sentences = MatchedSentence.objects.filter(
                officers__in=department.officers.all()
            ).all()

            featured_news_articles = (
                NewsArticle.objects.filter(matched_sentences__in=matched_sentences)
                .exclude(
                    id__in=starred_news_articles,
                )
                .distinct()
            )

            sorted_featured_news_articles = (
                NewsArticle.objects.select_related("source")
                .filter(
                    id__in=featured_news_articles,
                    is_hidden=False,
                )
                .annotate(is_starred=Value(False, output_field=BooleanField()))
                .order_by("-published_date")[
                    : DEPARTMENTS_LIMIT - starred_news_articles_count
                ]
            )

        news_articles = list(
            chain(starred_news_articles, sorted_featured_news_articles)
        )

        news_articles_serializers = DepartmentNewsArticleSerializer(
            news_articles, many=True
        )

        return Response(news_articles_serializers.data)

    @action(detail=True, methods=["get"], url_path="datasets")
    @custom_cache
    def datasets(self, request, pk):
        department = get_object_or_404(Department, slug=pk)
        wrgl_serializers = WrglFileSerializer(
            department.wrgl_files.order_by("position"), many=True
        )

        return Response(wrgl_serializers.data)

    @action(detail=False, methods=["get"], url_path="migratory")
    @custom_cache
    def migratory(self, request):
        officer_movements = (
            OfficerMovement.objects.select_related(
                "start_department",
                "end_department",
                "officer",
            )
            .filter(
                start_department__location__isnull=False,
                end_department__location__isnull=False,
            )
            .order_by(
                "date",
            )
        )

        graphs = OfficerMovementSerializer(officer_movements, many=True).data
        nodes = self._get_nodes(officer_movements)

        return Response(
            {
                "nodes": nodes,
                "graphs": graphs,
            }
        )

    @action(detail=True, methods=["get"], url_path="migratory-by-department")
    @custom_cache
    def migratory_by_department(self, request, pk):
        department = get_object_or_404(Department, slug=pk)

        officer_movements = (
            OfficerMovement.objects.select_related(
                "start_department",
                "end_department",
                "officer",
            )
            .filter(
                Q(start_department__location__isnull=False),
                Q(end_department__location__isnull=False),
                Q(start_department=department) | Q(end_department=department),
            )
            .annotate(
                is_left=Case(
                    When(start_department=department, then=True),
                    output_field=BooleanField(),
                    default=False,
                )
            )
            .order_by(
                "date",
            )
        )

        graphs = OfficerMovementSerializer(officer_movements, many=True).data
        nodes = self._get_nodes(officer_movements)

        return Response(
            {
                "nodes": nodes,
                "graphs": graphs,
            }
        )

    def _get_nodes(self, officer_movements):
        start_departments = officer_movements.values_list(
            "start_department__id", flat=True
        )
        end_departments = officer_movements.values_list("end_department__id", flat=True)
        department_ids = list(set(chain(start_departments, end_departments)))
        departments = Department.objects.filter(id__in=department_ids).order_by("slug")

        nodes = {}

        for department in departments:
            nodes[department.slug] = {
                "name": department.name,
                "location": department.location,
            }

        return nodes
