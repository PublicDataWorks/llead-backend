from django.db.models import Prefetch, Q

from appeals.models import Appeal
from complaints.models import Complaint
from departments.models import Department
from documents.models import Document
from news_articles.models import MatchedSentence, NewsArticle
from officers.constants import (
    COMPLAINT_ALL_EVENTS,
    OFFICER_DEPT,
    OFFICER_HIRE,
    OFFICER_LEFT,
    OFFICER_PAY_EFFECTIVE,
    OFFICER_RANK,
)
from officers.models import Event
from officers.serializers import (
    AppealTimelineSerializer,
    ComplaintTimelineSerializer,
    DocumentTimelineSerializer,
    JoinedTimelineSerializer,
    LeftTimelineSerializer,
    NewsArticleTimelineSerializer,
    RankChangeTimelineSerializer,
    SalaryChangeTimelineSerializer,
    UnitChangeTimelineSerializer,
    UseOfForceTimelineSerializer,
)
from use_of_forces.models import UseOfForceOfficer
from utils.data_utils import format_data_period, sort_items


class OfficerTimelineQuery(object):
    def __init__(self, officer):
        self.all_officers = officer.person.officers.all()

    @staticmethod
    def _filter_event_changes(events, compared_fields):
        sorted_events = sort_items(events, ["year", "month", "day"] + compared_fields)
        have_year_events = [event for event in sorted_events if event.year]
        no_year_events = [event for event in sorted_events if not event.year]

        previous_event = None
        previous_value = None
        changes = []

        for event in have_year_events:
            compared_value = [
                getattr(event, compared_field) for compared_field in compared_fields
            ]

            if compared_value != previous_value:
                if previous_event:
                    for field in compared_fields:
                        setattr(event, f"prev_{field}", getattr(previous_event, field))
                changes.append(event)
                previous_event = event
                previous_value = compared_value

        previous_value = None
        for event in no_year_events:
            compared_value = [
                getattr(event, compared_field) for compared_field in compared_fields
            ]
            if compared_value != previous_value:
                changes.append(event)
                previous_value = compared_value

        return changes

    @property
    def _complaint_timeline(self):
        complaint_timeline_queryset = Complaint.objects.prefetch_related(
            Prefetch(
                "events",
                queryset=Event.objects.filter(kind__in=COMPLAINT_ALL_EVENTS),
                to_attr="prefetched_receive_events",
            ),
        ).filter(officers__in=self.all_officers)

        return ComplaintTimelineSerializer(complaint_timeline_queryset, many=True).data

    @property
    def _use_of_force_timeline(self):
        use_of_force_officer_queryset = UseOfForceOfficer.objects.prefetch_related(
            "use_of_force__uof_citizens",
            "use_of_force__events",
        ).filter(officer__in=self.all_officers)

        return UseOfForceTimelineSerializer(
            use_of_force_officer_queryset, many=True
        ).data

    @property
    def _appeal_timeline(self):
        appeal_timeline_queryset = Appeal.objects.prefetch_related("events").filter(
            officer__in=self.all_officers
        )

        return AppealTimelineSerializer(appeal_timeline_queryset, many=True).data

    @property
    def _join_timeline(self):
        joined_timeline_query = Event.objects.select_related("department").filter(
            kind=OFFICER_HIRE,
            officer__in=self.all_officers,
        )

        return JoinedTimelineSerializer(joined_timeline_query, many=True).data

    @property
    def _left_timeline(self):
        left_timeline_query = Event.objects.select_related("department").filter(
            kind=OFFICER_LEFT,
            officer__in=self.all_officers,
        )

        return LeftTimelineSerializer(left_timeline_query, many=True).data

    @property
    def _document_timeline(self):
        document_timeline_queryset = Document.objects.prefetch_departments().filter(
            officers__in=self.all_officers
        )

        return DocumentTimelineSerializer(document_timeline_queryset, many=True).data

    @property
    def _news_aticle_timeline(self):
        articles_ids = (
            MatchedSentence.objects.all()
            .filter(officers__in=self.all_officers)
            .values_list("article__id", flat=True)
        )

        news_article_timeline_queryset = (
            NewsArticle.objects.prefetch_related("source")
            .filter(id__in=articles_ids)
            .distinct()
        )

        return NewsArticleTimelineSerializer(
            news_article_timeline_queryset, many=True
        ).data

    @property
    def _salary_change_timeline(self):
        events = Event.objects.filter(kind=OFFICER_PAY_EFFECTIVE,).filter(
            salary__isnull=False,
            salary_freq__isnull=False,
            officer__in=self.all_officers,
        )

        salary_changes = self._filter_event_changes(events, ["salary", "salary_freq"])

        return SalaryChangeTimelineSerializer(salary_changes, many=True).data

    @property
    def _rank_change_timeline(self):
        events = Event.objects.filter(kind=OFFICER_RANK,).filter(
            Q(officer__in=self.all_officers)
            & (Q(rank_code__isnull=False) | Q(rank_desc__isnull=False)),
        )

        rank_changes = self._filter_event_changes(events, ["rank_code", "rank_desc"])

        return RankChangeTimelineSerializer(rank_changes, many=True).data

    @property
    def _unit_change_timeline(self):
        events = Event.objects.filter(kind=OFFICER_DEPT).filter(
            Q(officer__in=self.all_officers)
            & (Q(department_code__isnull=False) | Q(department_desc__isnull=False)),
        )

        unit_changes = self._filter_event_changes(
            events,
            ["department_code", "department_desc"],
        )

        return UnitChangeTimelineSerializer(unit_changes, many=True).data

    def _get_timeline_period(self, timeline):
        officer_timeline_period = sorted(
            list(set([i["year"] for i in timeline if i["year"]]))
        )

        if len(officer_timeline_period) > 1:
            start_year = officer_timeline_period[0]
            end_year = officer_timeline_period[-1]

            event_years = []
            events = Event.objects.filter(officer__in=self.all_officers)
            departments = (
                Department.objects.filter(events__in=events)
                .only("data_period")
                .distinct()
            )

            for department in departments:
                department_period = department.data_period
                event_years.extend(
                    year for year in department_period if start_year <= year <= end_year
                )

            officer_timeline_period.extend(list(event_years))

        return format_data_period(officer_timeline_period)

    def query(self):
        period_only_items = self._complaint_timeline + self._use_of_force_timeline

        timeline = (
            period_only_items
            + self._join_timeline
            + self._left_timeline
            + self._document_timeline
            + self._salary_change_timeline
            + self._rank_change_timeline
            + self._unit_change_timeline
            + self._news_aticle_timeline
            + self._appeal_timeline
        )

        timeline_period = self._get_timeline_period(period_only_items)

        return {"timeline": timeline, "timeline_period": timeline_period}
