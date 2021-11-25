from django.db.models import Prefetch, Q

from complaints.models import Complaint
from documents.models import Document
from news_articles.models import NewsArticle, MatchedSentence
from officers.serializers import (
    ComplaintTimelineSerializer,
    UseOfForceTimelineSerializer,
    JoinedTimelineSerializer,
    LeftTimelineSerializer,
    DocumentTimelineSerializer,
    SalaryChangeTimelineSerializer,
    RankChangeTimelineSerializer,
    UnitChangeTimelineSerializer,
    NewsArticleTimelineSerializer,
)
from officers.constants import (
    OFFICER_HIRE,
    OFFICER_LEFT,
    OFFICER_PAY_EFFECTIVE,
    OFFICER_RANK,
    COMPLAINT_RECEIVE,
    OFFICER_DEPT
)
from officers.models import Event
from use_of_forces.models import UseOfForce
from utils.data_utils import sort_items
from utils.data_utils import data_period


class OfficerTimelineQuery(object):
    def __init__(self, officer):
        self.all_officers = officer.person.officers.all()

    @staticmethod
    def _filter_event_changes(events, compared_fields):
        sorted_events = sort_items(
            events,
            ['year', 'month', 'day'] + compared_fields
        )
        have_year_events = [event for event in sorted_events if event.year]
        no_year_events = [event for event in sorted_events if not event.year]

        previous_event = None
        previous_value = None
        changes = []

        for event in have_year_events:
            compared_value = [getattr(event, compared_field) for compared_field in compared_fields]

            if compared_value != previous_value:
                if previous_event:
                    for field in compared_fields:
                        setattr(event, f'prev_{field}', getattr(previous_event, field))
                changes.append(event)
                previous_event = event
                previous_value = compared_value

        previous_value = None
        for event in no_year_events:
            compared_value = [getattr(event, compared_field) for compared_field in compared_fields]
            if compared_value != previous_value:
                changes.append(event)
                previous_value = compared_value

        return changes

    @property
    def _complaint_timeline(self):
        complaint_timeline_queryset = Complaint.objects.prefetch_related(
            Prefetch(
                'events',
                queryset=Event.objects.filter(kind=COMPLAINT_RECEIVE),
                to_attr='prefetched_receive_events'
            ),
        ).filter(officers__in=self.all_officers)

        return ComplaintTimelineSerializer(complaint_timeline_queryset, many=True).data

    @property
    def _use_of_force_timeline(self):
        use_of_force_timeline_queryset = UseOfForce.objects.prefetch_related('events').filter(officer__in=self.all_officers)

        return UseOfForceTimelineSerializer(use_of_force_timeline_queryset, many=True).data

    @property
    def _join_timeline(self):
        joined_timeline_query = Event.objects.select_related(
            'department'
        ).filter(
            kind=OFFICER_HIRE,
            officer__in=self.all_officers,
        )

        return JoinedTimelineSerializer(joined_timeline_query, many=True).data

    @property
    def _left_timeline(self):
        left_timeline_query = Event.objects.select_related(
            'department'
        ).filter(
            kind=OFFICER_LEFT,
            officer__in=self.all_officers,
        )

        return LeftTimelineSerializer(left_timeline_query, many=True).data

    @property
    def _document_timeline(self):
        document_timeline_queryset = Document.objects.prefetch_departments().filter(officers__in=self.all_officers)

        return DocumentTimelineSerializer(document_timeline_queryset, many=True).data

    @property
    def _news_aticle_timeline(self):
        articles_ids = MatchedSentence.objects.all().filter(
            officers__in=self.all_officers
        ).values_list('article__id', flat=True)

        news_article_timeline_queryset = NewsArticle.objects.prefetch_related('source').filter(
            id__in=articles_ids
        ).distinct()

        return NewsArticleTimelineSerializer(news_article_timeline_queryset, many=True).data

    @property
    def _salary_change_timeline(self):
        events = Event.objects.filter(
                kind=OFFICER_PAY_EFFECTIVE,
            ).filter(salary__isnull=False, salary_freq__isnull=False, officer__in=self.all_officers)

        salary_changes = self._filter_event_changes(
            events,
            ['salary', 'salary_freq']
        )

        return SalaryChangeTimelineSerializer(salary_changes, many=True).data

    @property
    def _rank_change_timeline(self):
        events = Event.objects.filter(
                kind=OFFICER_RANK,
            ).filter(
                Q(officer__in=self.all_officers) &
                (Q(rank_code__isnull=False) | Q(rank_desc__isnull=False)),
            )

        rank_changes = self._filter_event_changes(
            events,
            ['rank_code', 'rank_desc']
        )

        return RankChangeTimelineSerializer(rank_changes, many=True).data

    @property
    def _unit_change_timeline(self):
        events = Event.objects.filter(
                kind=OFFICER_DEPT
            ).filter(
                Q(officer__in=self.all_officers) &
                (Q(department_code__isnull=False) | Q(department_desc__isnull=False)),
            )

        unit_changes = self._filter_event_changes(
            events,
            ['department_code', 'department_desc'],
        )

        return UnitChangeTimelineSerializer(unit_changes, many=True).data

    def query(self):
        timeline = self._complaint_timeline + self._use_of_force_timeline \
               + self._join_timeline + self._left_timeline \
               + self._document_timeline + self._salary_change_timeline \
               + self._rank_change_timeline + self._unit_change_timeline \
               + self._news_aticle_timeline

        timeline_period = data_period([i["year"] for i in timeline if i["year"]])

        return {'timeline': timeline, 'timeline_period': timeline_period}
