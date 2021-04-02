from datetime import date

from django.test import TestCase

from officers.queries import OfficerTimelineQuery
from officers.factories import OfficerFactory, OfficerHistoryFactory
from complaints.factories import ComplaintFactory
from officers.constants import (
    JOINED_TIMELINE_TYPE,
    COMPLAINT_TIMELINE_TYPE,
    LEFT_TIMELINE_TYPE,
)


class OfficerTimelineQueryTestCase(TestCase):
    def test_query(self):
        officer = OfficerFactory()
        officer_history_1 = OfficerHistoryFactory(
            officer=officer,
            start_date=date(2018, 4, 8),
            hire_year=2018,
            end_date=date(2020, 4, 8),
            term_year=2020,
        )
        officer_history_2 = OfficerHistoryFactory(
            officer=officer,
            start_date=date(2020, 5, 9),
            hire_year=2020,
        )
        complaint_1 = ComplaintFactory(
            incident_date=date(2019, 5, 4),
            occur_year=2019
        )
        complaint_2 = ComplaintFactory(
            incident_date=None,
            occur_year=None
        )
        complaint_1.officers.add(officer)
        complaint_2.officers.add(officer)

        expected_result = [
            {
                'kind': COMPLAINT_TIMELINE_TYPE,
                'date': None,
                'year': None,
                'rule_violation': complaint_2.rule_violation,
                'paragraph_violation': complaint_2.paragraph_violation,
                'disposition': complaint_2.disposition,
                'action': complaint_2.action,
                'tracking_number': complaint_2.tracking_number,
            },
            {
                'kind': JOINED_TIMELINE_TYPE,
                'date': officer_history_1.start_date,
                'year': officer_history_1.hire_year,
            },
            {
                'kind': COMPLAINT_TIMELINE_TYPE,
                'date': complaint_1.incident_date,
                'year': complaint_1.occur_year,
                'rule_violation': complaint_1.rule_violation,
                'paragraph_violation': complaint_1.paragraph_violation,
                'disposition': complaint_1.disposition,
                'action': complaint_1.action,
                'tracking_number': complaint_1.tracking_number,
            },
            {
                'kind': LEFT_TIMELINE_TYPE,
                'date': officer_history_1.end_date,
                'year': officer_history_1.term_year,
            },
            {
                'kind': JOINED_TIMELINE_TYPE,
                'date': officer_history_2.start_date,
                'year': officer_history_2.hire_year,
            },
        ]
        result = sorted(
            OfficerTimelineQuery(officer).query(),
            key=lambda item: str(item['date']) if item['date'] else ''
        )

        assert result == expected_result
