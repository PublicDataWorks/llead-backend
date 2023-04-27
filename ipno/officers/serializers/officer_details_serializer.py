from rest_framework import serializers

from documents.models import Document
from news_articles.models import MatchedSentence, NewsArticle
from officers.constants import UOF_OCCUR
from officers.models import Event
from shared.serializers import SimpleDepartmentSerializer


class OfficerDetailsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    badges = serializers.SerializerMethodField()
    birth_year = serializers.IntegerField()
    race = serializers.CharField()
    sex = serializers.CharField()

    departments = serializers.SerializerMethodField()
    salary = serializers.SerializerMethodField()
    salary_freq = serializers.SerializerMethodField()
    documents_count = serializers.SerializerMethodField()
    award_count = serializers.SerializerMethodField()
    articles_count = serializers.SerializerMethodField()
    articles_documents_years = serializers.SerializerMethodField()
    complaints_count = serializers.SerializerMethodField()
    sustained_complaints_count = serializers.SerializerMethodField()
    complaints_year_count = serializers.SerializerMethodField()
    incident_force_count = serializers.SerializerMethodField()
    termination_count = serializers.SerializerMethodField()
    latest_rank = serializers.SerializerMethodField()

    def _termination_left_reason(self, obj):
        if not hasattr(obj, "termination"):
            termination = Event.objects.filter(
                left_reason__icontains="terminat"
            ).values_list("left_reason", flat=True)
            setattr(obj, "termination", set(termination))

        return obj.termination

    def _get_person_officers(self, obj):
        if not hasattr(obj, "person_officers"):
            person_officers = obj.person.officers.all()
            setattr(obj, "person_officers", person_officers)

        return obj.person_officers

    def _get_all_events(self, obj):
        if not hasattr(obj, "all_events"):
            all_officers = self._get_person_officers(obj)

            all_events = []
            for officer in all_officers:
                all_events.extend(officer.events.all())

            all_events.sort(
                key=lambda k: (
                    (k.year is None, -k.year if k.year is not None else None),
                    (k.month is None, -k.month if k.month is not None else None),
                    (k.day is None, -k.day if k.day is not None else None),
                )
            )

            setattr(obj, "all_events", all_events)

        return obj.all_events

    def _get_first_salary_event(self, obj):
        if not hasattr(obj, "first_salary_event"):
            all_events = self._get_all_events(obj)

            first_salary_event = None
            for event in all_events:
                if event.salary and event.salary_freq:
                    first_salary_event = event
                    break

            setattr(obj, "first_salary_event", first_salary_event)

        return obj.first_salary_event

    def get_badges(self, obj):
        all_events = self._get_all_events(obj)

        events = list(
            dict.fromkeys([event.badge_no for event in all_events if event.badge_no])
        )
        return events

    def get_departments(self, obj):
        canonical_dep = obj.person.canonical_officer.department

        all_events = self._get_all_events(obj)

        all_departments = {event.department for event in all_events}
        raw_departments = list(dict.fromkeys([canonical_dep, *all_departments]))
        departments = [
            department for department in raw_departments if department is not None
        ]

        return SimpleDepartmentSerializer(departments, many=True).data

    def get_salary(self, obj):
        salary_event = self._get_first_salary_event(obj)
        salary_field = serializers.DecimalField(max_digits=8, decimal_places=2)
        return (
            salary_field.to_representation(salary_event.salary)
            if salary_event
            else None
        )

    def get_salary_freq(self, obj):
        salary_event = self._get_first_salary_event(obj)
        return salary_event.salary_freq if salary_event else None

    def get_documents_count(self, obj):
        officers = self._get_person_officers(obj)

        return sum([obj.documents.count() for obj in officers])

    def get_articles_count(self, obj):
        officers = self._get_person_officers(obj)
        matched_sentences = []

        for officer in officers:
            if officer.matched_sentences.count() > 0:
                matched_sentences.extend(officer.matched_sentences.all())

        return (
            NewsArticle.objects.filter(matched_sentences__in=matched_sentences)
            .distinct()
            .count()
        )

    def get_complaints_count(self, obj):
        return obj.person.all_complaints_count

    def get_sustained_complaints_count(self, obj):
        officers = self._get_person_officers(obj)

        return sum([len(officer.sustained_complaints) for officer in officers])

    def get_complaints_year_count(self, obj):
        all_events = self._get_all_events(obj)
        years = [
            event.year
            for event in all_events
            if event.year and event.complaints.count() > 0
        ]

        return years[0] - years[-1] if len(years) > 1 else len(years)

    def get_incident_force_count(self, obj):
        all_events = self._get_all_events(obj)

        incident_forces = [
            event.kind for event in all_events if event.kind == UOF_OCCUR
        ]

        return len(incident_forces)

    def get_termination_count(self, obj):
        all_events = self._get_all_events(obj)
        terminations = self._termination_left_reason(obj)

        return len([event for event in all_events if event.left_reason in terminations])

    def get_latest_rank(self, obj):
        events = self._get_all_events(obj)

        rank_events = [rank for rank in events if rank.rank_desc]

        return rank_events[0].rank_desc if rank_events else None

    def get_articles_documents_years(self, obj):
        officers = self._get_person_officers(obj)
        years = []

        matched_sentences = MatchedSentence.objects.filter(officers__in=officers)
        articles = NewsArticle.objects.filter(matched_sentences__in=matched_sentences)
        if articles:
            articles_dates = articles.values_list("published_date", flat=True)
            articles_years = [date.year for date in articles_dates]
            years.extend(articles_years)

        documents = Document.objects.filter(officers__in=officers)
        if documents:
            documents_years = documents.filter(year__isnull=False).values_list(
                "year", flat=True
            )
            years.extend(list(documents_years))

        return sorted(list(set(years)))

    def get_award_count(self, obj):
        events = self._get_all_events(obj)

        awards = [event.award for event in events if event.award]

        return len(awards)
