from datetime import date

from django.test import TestCase

from officers.queries import OfficerTimelineQuery
from officers.factories import OfficerFactory, OfficerHistoryFactory
from complaints.factories import ComplaintFactory
from documents.factories import DocumentFactory
from departments.factories import DepartmentFactory
from officers.constants import (
    JOINED_TIMELINE_KIND,
    COMPLAINT_TIMELINE_KIND,
    LEFT_TIMELINE_KIND,
    DOCUMENT_TIMELINE_KIND,
    SALARY_CHANGE_TIMELINE_KIND
)


class OfficerTimelineQueryTestCase(TestCase):
    def test_query(self):
        officer = OfficerFactory()
        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()
        officer_history_1 = OfficerHistoryFactory(
            officer=officer,
            start_date=date(2018, 4, 8),
            hire_year=2018,
            end_date=date(2020, 4, 8),
            term_year=2020,
            department=department_1,
            annual_salary='57k',
            pay_effective_year=2019,
            pay_effective_month=12,
            pay_effective_day=1,
        )
        officer_history_2 = OfficerHistoryFactory(
            officer=officer,
            start_date=date(2020, 5, 9),
            hire_year=2020,
            department=department_2,
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

        document_1 = DocumentFactory(incident_date=date(2018, 6, 5))
        document_2 = DocumentFactory(incident_date=date(2021, 2, 1))

        document_1.officers.add(officer)
        document_2.officers.add(officer)
        document_1.departments.add(department_1)

        expected_result = [
            {
                'kind': COMPLAINT_TIMELINE_KIND,
                'date': None,
                'year': None,
                'rule_violation': complaint_2.rule_violation,
                'paragraph_violation': complaint_2.paragraph_violation,
                'disposition': complaint_2.disposition,
                'action': complaint_2.action,
                'tracking_number': complaint_2.tracking_number,
            },
            {
                'kind': JOINED_TIMELINE_KIND,
                'date': str(officer_history_1.start_date),
                'year': officer_history_1.hire_year,
            },
            {
                'kind': DOCUMENT_TIMELINE_KIND,
                'date': str(document_1.incident_date),
                'id': document_1.id,
                'document_type': document_1.document_type,
                'title': document_1.title,
                'url': document_1.url,
                'preview_image_url': document_1.preview_image_url,
                'incident_date': str(document_1.incident_date),
                'pages_count': document_1.pages_count,
                'departments': [
                    {
                        'id': department_1.id,
                        'name': department_1.name,
                    },
                ],
            },
            {
                'kind': COMPLAINT_TIMELINE_KIND,
                'date': str(complaint_1.incident_date),
                'year': complaint_1.occur_year,
                'rule_violation': complaint_1.rule_violation,
                'paragraph_violation': complaint_1.paragraph_violation,
                'disposition': complaint_1.disposition,
                'action': complaint_1.action,
                'tracking_number': complaint_1.tracking_number,
            },
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'annual_salary': '57k',
                'date': date(2019, 12, 1),
                'year': 2019,
            },
            {
                'kind': LEFT_TIMELINE_KIND,
                'date': str(officer_history_1.end_date),
                'year': officer_history_1.term_year,
            },
            {
                'kind': JOINED_TIMELINE_KIND,
                'date': str(officer_history_2.start_date),
                'year': officer_history_2.hire_year,
            },
            {
                'kind': DOCUMENT_TIMELINE_KIND,
                'date': str(document_2.incident_date),
                'id': document_2.id,
                'document_type': document_2.document_type,
                'title': document_2.title,
                'url': document_2.url,
                'preview_image_url': document_2.preview_image_url,
                'incident_date': str(document_2.incident_date),
                'pages_count': document_2.pages_count,
                'departments': [],
            },
        ]
        result = sorted(
            OfficerTimelineQuery(officer).query(),
            key=lambda item: str(item['date']) if item['date'] else ''
        )

        assert result == expected_result

    def test_salary_change(self):
        officer = OfficerFactory()
        OfficerHistoryFactory(
            officer=officer,
            annual_salary='57k',
            pay_effective_year=2015,
            pay_effective_month=12,
            pay_effective_day=1,
            start_date=None
        )
        OfficerHistoryFactory(
            officer=officer,
            annual_salary='65k',
            pay_effective_year=2019,
            pay_effective_month=3,
            pay_effective_day=7,
            start_date=None
        )
        OfficerHistoryFactory(
            officer=officer,
            annual_salary='57k',
            pay_effective_year=2017,
            pay_effective_month=5,
            pay_effective_day=6,
            start_date=None
        )
        OfficerHistoryFactory(
            officer=officer,
            annual_salary='45k',
            pay_effective_year=None,
            start_date=None
        )
        OfficerHistoryFactory(
            officer=officer,
            annual_salary='45k',
            pay_effective_year=None,
            start_date=None
        )
        OfficerHistoryFactory(
            officer=officer,
            annual_salary='60k',
            pay_effective_year=None,
            start_date=None
        )
        OfficerHistoryFactory(
            officer=officer,
            annual_salary='45k',
            pay_effective_year=2019,
            start_date=None
        )

        expected_result = [
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'annual_salary': '45k',
                'date': None,
                'year': 2019,
            },
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'annual_salary': '45k',
                'date': None,
                'year': None,
            },
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'annual_salary': '60k',
                'date': None,
                'year': None,
            },
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'annual_salary': '57k',
                'date': date(2015, 12, 1),
                'year': 2015,
            },
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'annual_salary': '65k',
                'date': date(2019, 3, 7),
                'year': 2019,
            },

        ]
        result = sorted(
            OfficerTimelineQuery(officer).query(),
            key=lambda item: str(item['date']) if item['date'] else ''
        )

        assert result == expected_result
