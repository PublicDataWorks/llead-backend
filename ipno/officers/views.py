from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from officers.constants import (
    OFFICER_DEPT,
    OFFICER_HIRE,
    OFFICER_LEFT,
    OFFICER_PAY_EFFECTIVE,
    OFFICER_RANK,
    OFFICERS_LIMIT,
)
from officers.models import Officer
from officers.queries import OfficerDatafileQuery, OfficerTimelineQuery
from officers.serializers import OfficerDetailsSerializer
from shared.serializers import OfficerSerializer
from utils.cache_utils import custom_cache
from utils.decorators import test_util_api


class OfficersViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @custom_cache
    def list(self, request):
        officers = (
            Officer.objects.prefetch_events()
            .select_related("person__canonical_officer__department")
            .filter(canonical_person__isnull=False)
            .order_by("-person__all_complaints_count")[:OFFICERS_LIMIT]
        )

        serializer = OfficerSerializer(officers, many=True)
        return Response(serializer.data)

    @custom_cache
    def retrieve(self, request, pk):
        officer = get_object_or_404(
            Officer.objects.prefetch_related("person__canonical_officer"), id=pk
        )
        serializer = OfficerDetailsSerializer(officer.person.canonical_officer)

        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="timeline")
    @custom_cache
    def timeline(self, request, pk):
        officer = get_object_or_404(
            Officer.objects.prefetch_related("person__officers"), id=pk
        )

        return Response(OfficerTimelineQuery(officer).query())

    @action(detail=True, methods=["get"], url_path="download-xlsx")
    def download_xlsx(self, request, pk):
        officer = get_object_or_404(Officer, id=pk)

        excel_file = OfficerDatafileQuery(officer).generate_sheets_file()
        filename = f"officer-{pk}.xlsx"

        response = HttpResponse(
            excel_file.getvalue(),
            content_type=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"

        return response

    @test_util_api
    @action(detail=False, methods=["get"], url_path="testing-officer-timelines")
    def testing_officer_timelines(self, request):
        complaint_timeline_officer_id = (
            Officer.objects.filter(
                complaints__allegation__isnull=False,
                complaints__disposition__isnull=False,
                complaints__allegation_desc__isnull=False,
                complaints__action__isnull=False,
                complaints__tracking_id__isnull=False,
            )
            .first()
            .id
        )
        uof_timeline_officer_id = (
            Officer.objects.filter(
                use_of_forces__use_of_force_reason__isnull=False,
                use_of_forces__disposition__isnull=False,
                use_of_forces__service_type__isnull=False,
                use_of_forces__tracking_id__isnull=False,
                use_of_forces__uof_citizens__isnull=False,
            )
            .first()
            .id
        )
        hire_and_left_timeline_officer_id = (
            Officer.objects.filter(events__kind__in=[OFFICER_HIRE, OFFICER_LEFT])
            .annotate(Count("id"))
            .order_by()
            .filter(id__count__gt=1)
            .first()
            .id
        )
        document_timeline_officer_id = (
            Officer.objects.filter(documents__isnull=False).first().id
        )
        salary_change_timeline_officer_id = (
            Officer.objects.filter(
                events__kind=OFFICER_PAY_EFFECTIVE,
                events__salary__isnull=False,
                events__salary_freq__isnull=False,
            )
            .first()
            .id
        )
        rank_change_timeline_officer_id = (
            Officer.objects.filter(
                events__kind=OFFICER_RANK,
                events__rank_code__isnull=False,
                events__rank_desc__isnull=False,
            )
            .first()
            .id
        )
        unit_change_timeline_officer_id = (
            Officer.objects.filter(
                events__kind=OFFICER_DEPT,
                events__department_code__isnull=False,
                events__department_desc__isnull=False,
            )
            .first()
            .id
        )
        news_article_timeline_officer_id = (
            Officer.objects.filter(matched_sentences__isnull=False).first().id
        )
        appeal_timeline_officer_id = (
            Officer.objects.filter(appeals__isnull=False).first().id
        )

        response = {
            "complaint_officer_id": complaint_timeline_officer_id,
            "uof_officer_id": uof_timeline_officer_id,
            "hire_and_left_officer_id": hire_and_left_timeline_officer_id,
            "document_officer_id": document_timeline_officer_id,
            "salary_change_officer_id": salary_change_timeline_officer_id,
            "rank_change_officer_id": rank_change_timeline_officer_id,
            "unit_change_officer_id": unit_change_timeline_officer_id,
            "news_article_officer_id": news_article_timeline_officer_id,
            "appeal_officer_id": appeal_timeline_officer_id,
        }
        return Response(response)
