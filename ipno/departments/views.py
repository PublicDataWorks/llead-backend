from itertools import chain

from django.conf import settings
from django.db.models import Count, BooleanField, Prefetch, Sum
from django.db.models.expressions import F, Value, Case, When
from django.db.models.fields import IntegerField
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework.decorators import action

from departments.models import Department
from departments.serializers import (
    WrglFileSerializer,
    DepartmentOfficerSerializer,
    DepartmentNewsArticleSerializer,
    DepartmentDocumentSerializer,
    DepartmentCoordinateSerializer,
)
from documents.models import Document
from news_articles.models import MatchedSentence, NewsArticle
from officers.constants import OFFICER_LEFT, OFFICER_HIRE
from officers.models import Officer, Event
from people.models import Person
from shared.serializers import DepartmentSerializer
from utils.es_pagination import ESPagination
from utils.parse_utils import parse_date
from departments.serializers import DepartmentDetailsSerializer
from departments.constants import DEPARTMENTS_LIMIT
from search.queries import (
    OfficersSearchQuery,
    NewsArticlesSearchQuery,
    DocumentsSearchQuery)
from departments.serializers.es_serializers import (
    DepartmentOfficersESSerializer,
    DepartmentNewsArticlesESSerializer,
    DepartmentDocumentsESSerializer,
)


class DepartmentsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(settings.VIEW_CACHING_TIME))
    @cache_control(no_store=True)
    def retrieve(self, request, pk):
        queryset = Department.objects.all()
        department = get_object_or_404(queryset, slug=pk)
        serializer = DepartmentDetailsSerializer(department)

        return Response(serializer.data)

    @method_decorator(cache_page(settings.VIEW_CACHING_TIME))
    @cache_control(no_store=True)
    def list(self, request):
        departments = Department.objects.exclude(
                complaints__isnull=True,
                use_of_forces__isnull=True,
                documents__isnull=True,
            ).annotate(
                officersCount=Count('officers__id', distinct=True)
        ).order_by('-officersCount')[:DEPARTMENTS_LIMIT]
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='search')
    def search(self, request, pk):
        q = self.request.query_params.get('q', '')
        kind = self.request.query_params.get('kind', '')

        serializer_mapping = {
            'officers': DepartmentOfficersESSerializer,
            'news_articles': DepartmentNewsArticlesESSerializer,
            'documents': DepartmentDocumentsESSerializer,
        }

        search_query_mapping = {
            'officers': OfficersSearchQuery,
            'news_articles': NewsArticlesSearchQuery,
            'documents': DocumentsSearchQuery,
        }

        if kind not in serializer_mapping.keys():
            return Response(f'Missing kind param, must be in {serializer_mapping.keys()}', status=HTTP_400_BAD_REQUEST)

        search_query = search_query_mapping[kind](q, pk)

        paginator = ESPagination()
        page = paginator.paginate_es_query(search_query, request)

        data = serializer_mapping[kind](page).data

        return paginator.get_paginated_response(data)

    @action(detail=True, methods=['get'], url_path='documents')
    @method_decorator(cache_page(settings.VIEW_CACHING_TIME))
    @cache_control(no_store=True)
    def documents(self, request, pk):
        department = get_object_or_404(Department, slug=pk)

        starred_documents = department.starred_documents.prefetch_related().annotate(
            is_starred=Value(True, output_field=BooleanField()),
        ).all()[:DEPARTMENTS_LIMIT]

        starred_documents_count = starred_documents.count()
        sorted_featured_documents = []

        if starred_documents_count < DEPARTMENTS_LIMIT:
            featured_documents = department.documents.exclude(
                id__in=starred_documents,
            )

            sorted_featured_documents = Document.objects.filter(
                id__in=featured_documents
            ).annotate(
                is_starred=Value(False, output_field=BooleanField()),
            ).order_by('-incident_date')[:DEPARTMENTS_LIMIT - starred_documents_count]

        documents = list(chain(starred_documents, sorted_featured_documents))

        documents_serializers = DepartmentDocumentSerializer(documents, many=True)

        return Response(documents_serializers.data)

    @action(detail=True, methods=['get'], url_path='officers')
    @method_decorator(cache_page(settings.VIEW_CACHING_TIME))
    @cache_control(no_store=True)
    def officers(self, request, pk):
        department = get_object_or_404(Department, slug=pk)

        other_prefetches = (
            Prefetch(
                'department'
            ),
        )

        starred_officers = department.starred_officers.prefetch_events(other_prefetches).annotate(
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

            sorted_featured_officers = Officer.objects.prefetch_events(other_prefetches).filter(
                id__in=featured_officers
            ).annotate(
                is_starred=Value(False, output_field=BooleanField()),
                use_of_forces_count=Count('use_of_forces'),
            ).order_by('-person__all_complaints_count')[:DEPARTMENTS_LIMIT - starred_officers_count]

        officers = list(chain(starred_officers, sorted_featured_officers))

        officers_serializers = DepartmentOfficerSerializer(officers, many=True)

        return Response(officers_serializers.data)

    @action(detail=True, methods=['get'], url_path='news_articles')
    @method_decorator(cache_page(settings.VIEW_CACHING_TIME))
    @cache_control(no_store=True)
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
    @method_decorator(cache_page(settings.VIEW_CACHING_TIME))
    @cache_control(no_store=True)
    def datasets(self, request, pk):
        department = get_object_or_404(Department, slug=pk)
        wrgl_serializers = WrglFileSerializer(department.wrgl_files.order_by('position'), many=True)

        return Response(wrgl_serializers.data)

    @action(detail=False, methods=['get'], url_path='migratory')
    @method_decorator(cache_page(settings.VIEW_CACHING_TIME))
    @cache_control(no_store=True)
    def migratory(self, request):
        have_left_hire_officers = Officer.objects.annotate(
            left_count=Sum(Case(When(events__kind=OFFICER_LEFT, then=1), output_field=IntegerField())),
            hire_count=Sum(Case(When(events__kind=OFFICER_HIRE, then=1), output_field=IntegerField())),
        ).filter(left_count__gt=0, hire_count__gt=0)

        people = Person.objects.prefetch_related(
            'officers',
            Prefetch(
                'officers__events',
                queryset=Event.objects.order_by(
                    F('year').desc(nulls_last=True),
                    F('month').desc(nulls_last=True),
                    F('day').desc(nulls_last=True),
                ).filter(
                    kind__in=[OFFICER_LEFT, OFFICER_HIRE],
                    department__location__isnull=False,
                ).select_related('officer', 'department'),
                to_attr='prefetch_hire_left_events'
            ),
        ).filter(officers__in=have_left_hire_officers).distinct()
        migrated_officers = []
        graphs = []

        migrated_department = set()

        for person in people:
            officers = person.officers.all()
            hire_left_events = {}

            for officer in officers:
                hire_left_officer_events = officer.prefetch_hire_left_events
                for event in hire_left_officer_events:
                    event_date = parse_date(event.year, event.month, event.day)

                    if event_date and (event.officer.id, event_date, event.kind) not in hire_left_events:
                        hire_left_events[(event.officer.id, event_date, event.kind)] = (event_date, event)

            hire_left_dates = list(hire_left_events.values())
            hire_left_dates.sort(key=lambda x: x[0])
            lines = []

            for index in range(0, len(hire_left_dates) - 1):
                if hire_left_dates[index][1].department != hire_left_dates[index + 1][1].department and \
                        hire_left_dates[index][1].kind == OFFICER_LEFT and \
                        hire_left_dates[index + 1][1].kind == OFFICER_HIRE:
                    lines.append((hire_left_dates[index], hire_left_dates[index+1]))

            if len(lines) > 0:
                migrated_officers.append(officers[0])
                migratory_event = {}

                for line in lines:
                    migratory_event['start_node'] = line[0][1].department.slug
                    migratory_event['end_node'] = line[1][1].department.slug
                    migratory_event['start_location'] = line[0][1].department.location
                    migratory_event['end_location'] = line[1][1].department.location
                    migratory_event['year'] = line[1][1].year
                    migratory_event['date'] = line[1][0]
                    migratory_event['officer_name'] = line[0][1].officer.name
                    migratory_event['officer_id'] = line[0][1].officer.id
                    graphs.append(migratory_event)

                    migrated_department.add(line[0][1].department.slug)
                    migrated_department.add(line[1][1].department.slug)

        graphs.sort(key=lambda obj: obj['date'])

        departments = Department.objects.filter(
            slug__in=migrated_department,
            location__isnull=False,
        ).order_by('slug').distinct()
        serialized_departments = DepartmentCoordinateSerializer(departments, many=True).data

        nodes = {}
        for department in serialized_departments:
            nodes[department['id']] = {
                'name': department['name'],
                'location': department['location']
            }

        return Response({
            "nodes": nodes,
            "graphs": graphs,
        })
