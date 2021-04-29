from datetime import date

from django.test import TestCase

from officers.queries import OfficerTimelineQuery
from officers.factories import OfficerFactory, EventFactory
from complaints.factories import ComplaintFactory
from documents.factories import DocumentFactory
from departments.factories import DepartmentFactory
from officers.constants import (
    JOINED_TIMELINE_KIND,
    COMPLAINT_TIMELINE_KIND,
    LEFT_TIMELINE_KIND,
    DOCUMENT_TIMELINE_KIND,
    SALARY_CHANGE_TIMELINE_KIND,
    RANK_CHANGE_TIMELINE_KIND,
    UNIT_CHANGE_TIMELINE_KIND,
)
from officers.constants import (
    OFFICER_HIRE,
    OFFICER_LEFT,
    OFFICER_PAY_EFFECTIVE,
    OFFICER_RANK,
    COMPLAINT_RECEIVE,
    OFFICER_DEPT,
)


class OfficerTimelineQueryTestCase(TestCase):
    def test_query(self):
        officer = OfficerFactory()
        department_1 = DepartmentFactory()
        department_2 = DepartmentFactory()
        complaint_1 = ComplaintFactory(allegation_finding='Sustained')
        complaint_2 = ComplaintFactory(allegation_finding='not sustained')
        complaint_3 = ComplaintFactory(allegation_finding='unfounded')
        complaint_4 = ComplaintFactory(allegation_finding='illegitimate outcome')
        for complaint in [complaint_1, complaint_2, complaint_3, complaint_4]:
            complaint.officers.add(officer)

        EventFactory(
            officer=officer,
            department=department_1,
            kind=OFFICER_HIRE,
            year=2018,
            month=4,
            day=8,
        )
        EventFactory(
            officer=officer,
            department=department_1,
            kind=OFFICER_LEFT,
            year=2020,
            month=4,
            day=8,
        )
        EventFactory(
            officer=officer,
            department=department_1,
            kind=OFFICER_PAY_EFFECTIVE,
            annual_salary='57000',
            year=2019,
            month=12,
            day=1,
        )
        EventFactory(
            officer=officer,
            department=department_2,
            kind=OFFICER_HIRE,
            year=2020,
            month=5,
            day=9,
        )
        EventFactory(
            officer=officer,
            department=department_2,
            kind=OFFICER_RANK,
            rank_desc='senior police office',
            rank_code=3,
            year=2017,
            month=7,
            day=13,
        )
        complaint_receive_event = EventFactory(
            officer=officer,
            department=department_1,
            kind=COMPLAINT_RECEIVE,
            year=2019,
            month=5,
            day=4,
        )
        complaint_1.events.add(complaint_receive_event)

        EventFactory(
            kind=OFFICER_DEPT,
            officer=officer,
            department=department_1,
            department_code='193',
            department_desc='Gang Investigation Division',
            year=2017,
            month=7,
            day=14,
        )
        EventFactory(
            kind=OFFICER_DEPT,
            officer=officer,
            department=department_1,
            department_code='610',
            department_desc='Detective Area - Central',
            year=2018,
            month=8,
            day=10,
        )

        document_1 = DocumentFactory(incident_date=date(2018, 6, 5))
        document_2 = DocumentFactory(incident_date=date(2021, 2, 1))

        document_1.officers.add(officer)
        document_2.officers.add(officer)
        document_1.departments.add(department_1)

        expected_result = [
            {
                'id': complaint_2.id,
                'kind': COMPLAINT_TIMELINE_KIND,
                'date': None,
                'year': None,
                'rule_code': complaint_2.rule_code,
                'rule_violation': complaint_2.rule_violation,
                'paragraph_code': complaint_2.paragraph_code,
                'paragraph_violation': complaint_2.paragraph_violation,
                'disposition': complaint_2.disposition,
                'action': complaint_2.action,
                'tracking_number': complaint_2.tracking_number,
            },
            {
                'kind': RANK_CHANGE_TIMELINE_KIND,
                'rank_code': '3',
                'rank_desc': 'senior police office',
                'date': str(date(2017, 7, 13)),
                'year': 2017,
            },
            {
                'kind': UNIT_CHANGE_TIMELINE_KIND,
                'department_code': '193',
                'department_desc': 'Gang Investigation Division',
                'prev_department_code': None,
                'prev_department_desc': None,
                'date': str(date(2017, 7, 14)),
                'year': 2017,
            },
            {
                'kind': JOINED_TIMELINE_KIND,
                'date': str(date(2018, 4, 8)),
                'year': 2018,
            },
            {
                'kind': DOCUMENT_TIMELINE_KIND,
                'date': str(document_1.incident_date),
                'year': document_1.incident_date.year,
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
                'kind': UNIT_CHANGE_TIMELINE_KIND,
                'department_code': '610',
                'department_desc': 'Detective Area - Central',
                'prev_department_code': '193',
                'prev_department_desc': 'Gang Investigation Division',
                'date': str(date(2018, 8, 10)),
                'year': 2018,
            },
            {
                'id': complaint_1.id,
                'kind': COMPLAINT_TIMELINE_KIND,
                'date': str(date(2019, 5, 4)),
                'year': 2019,
                'rule_code': complaint_1.rule_code,
                'rule_violation': complaint_1.rule_violation,
                'paragraph_code': complaint_1.paragraph_code,
                'paragraph_violation': complaint_1.paragraph_violation,
                'disposition': complaint_1.disposition,
                'action': complaint_1.action,
                'tracking_number': complaint_1.tracking_number,
            },
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'annual_salary': '57000',
                'hourly_salary': None,
                'date': str(date(2019, 12, 1)),
                'year': 2019,
            },
            {
                'kind': LEFT_TIMELINE_KIND,
                'date': str(date(2020, 4, 8)),
                'year': 2020,
            },
            {
                'kind': JOINED_TIMELINE_KIND,
                'date': str(date(2020, 5, 9)),
                'year': 2020,
            },
            {
                'kind': DOCUMENT_TIMELINE_KIND,
                'date': str(document_2.incident_date),
                'year': document_2.incident_date.year,
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
        EventFactory(
            officer=officer,
            kind=OFFICER_PAY_EFFECTIVE,
            annual_salary='57000',
            year=2015,
            month=12,
            day=1,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_PAY_EFFECTIVE,
            annual_salary='65000',
            year=2019,
            month=3,
            day=7,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_PAY_EFFECTIVE,
            annual_salary='57000',
            year=2017,
            month=5,
            day=6,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_PAY_EFFECTIVE,
            annual_salary='45000',
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_PAY_EFFECTIVE,
            annual_salary='45000',
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_PAY_EFFECTIVE,
            annual_salary='60000',
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_PAY_EFFECTIVE,
            annual_salary='45000',
            year=2019,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_PAY_EFFECTIVE,
            hourly_salary='26.14',
            year=2017,
            month=8,
            day=12,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_PAY_EFFECTIVE,
            hourly_salary='16.15',
            year=None,
            month=None,
            day=None,
        )

        expected_result = [
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'annual_salary': '57000',
                'hourly_salary': None,
                'date': str(date(2015, 12, 1)),
                'year': 2015,
            },
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'annual_salary': None,
                'hourly_salary': '26.14',
                'date': str(date(2017, 8, 12)),
                'year': 2017,
            },
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'annual_salary': '65000',
                'hourly_salary': None,
                'date': str(date(2019, 3, 7)),
                'year': 2019,
            },
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'annual_salary': '45000',
                'hourly_salary': None,
                'date': None,
                'year': 2019,
            },
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'annual_salary': '45000',
                'hourly_salary': None,
                'date': None,
                'year': None,
            },
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'annual_salary': '60000',
                'hourly_salary': None,
                'date': None,
                'year': None,
            },
            {
                'kind': SALARY_CHANGE_TIMELINE_KIND,
                'annual_salary': None,
                'hourly_salary': '16.15',
                'date': None,
                'year': None,
            },
        ]

        assert OfficerTimelineQuery(officer).query() == expected_result

    def test_rank_change(self):
        officer = OfficerFactory()
        EventFactory(
            officer=officer,
            kind=OFFICER_RANK,
            rank_desc='Fresh Officer',
            rank_code='1',
            year=2015,
            month=12,
            day=1,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_RANK,
            rank_desc='Senior Officer',
            rank_code='3',
            year=2019,
            month=3,
            day=7,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_RANK,
            rank_desc='Fresh Officer',
            rank_code='1',
            year=2017,
            month=5,
            day=6,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_RANK,
            rank_desc='Junior Officer',
            rank_code='2',
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_RANK,
            rank_desc='Junior Officer',
            rank_code='2',
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_RANK,
            rank_desc='Senior Officer',
            rank_code='3',
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_RANK,
            rank_desc='Junior Officer',
            rank_code='2',
            year=2019,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_RANK,
            rank_desc='police recruit',
            rank_code=None,
            year=2017,
            month=8,
            day=12,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_RANK,
            rank_desc='police technical specialist',
            rank_code=None,
            year=None,
            month=None,
            day=None,
        )

        expected_result = [
            {
                'kind': RANK_CHANGE_TIMELINE_KIND,
                'rank_desc': 'Fresh Officer',
                'rank_code': '1',
                'date': str(date(2015, 12, 1)),
                'year': 2015,
            },
            {
                'kind': RANK_CHANGE_TIMELINE_KIND,
                'rank_desc': 'police recruit',
                'rank_code': None,
                'date': str(date(2017, 8, 12)),
                'year': 2017,
            },
            {
                'kind': RANK_CHANGE_TIMELINE_KIND,
                'rank_desc': 'Senior Officer',
                'rank_code': '3',
                'date': str(date(2019, 3, 7)),
                'year': 2019,
            },
            {
                'kind': RANK_CHANGE_TIMELINE_KIND,
                'rank_desc': 'Junior Officer',
                'rank_code': '2',
                'date': None,
                'year': 2019,
            },
            {
                'kind': RANK_CHANGE_TIMELINE_KIND,
                'rank_desc': 'Junior Officer',
                'rank_code': '2',
                'date': None,
                'year': None,
            },
            {
                'kind': RANK_CHANGE_TIMELINE_KIND,
                'rank_desc': 'Senior Officer',
                'rank_code': '3',
                'date': None,
                'year': None,
            },
            {
                'kind': RANK_CHANGE_TIMELINE_KIND,
                'rank_desc': 'police technical specialist',
                'rank_code': None,
                'date': None,
                'year': None,
            },
        ]

        assert OfficerTimelineQuery(officer).query() == expected_result

    def test_unit_change(self):
        officer = OfficerFactory()
        EventFactory(
            officer=officer,
            kind=OFFICER_DEPT,
            department_code='193',
            department_desc='Gang Investigation Division',
            year=2015,
            month=12,
            day=1,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_DEPT,
            department_code='610',
            department_desc='Detective Area - Central',
            year=2019,
            month=3,
            day=7,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_DEPT,
            department_code='193',
            department_desc='Gang Investigation Division',
            year=2017,
            month=5,
            day=6,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_DEPT,
            department_code='5020',
            department_desc='police-uniform patrol bureau',
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_DEPT,
            department_code='5020',
            department_desc='police-uniform patrol bureau',
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_DEPT,
            department_code='610',
            department_desc='Detective Area - Central',
            year=None,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_DEPT,
            department_code='5020',
            department_desc='police-uniform patrol bureau',
            year=2019,
            month=None,
            day=None,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_DEPT,
            department_code=None,
            department_desc='fob - field operations bureau',
            year=2017,
            month=8,
            day=12,
        )
        EventFactory(
            officer=officer,
            kind=OFFICER_DEPT,
            department_code=None,
            department_desc='msb - management service bureau',
            year=None,
            month=None,
            day=None,
        )

        expected_result = [
            {
                'kind': UNIT_CHANGE_TIMELINE_KIND,
                'department_code': '193',
                'department_desc': 'Gang Investigation Division',
                'prev_department_code': None,
                'prev_department_desc': None,
                'date': str(date(2015, 12, 1)),
                'year': 2015,
            },
            {
                'kind': UNIT_CHANGE_TIMELINE_KIND,
                'department_code': None,
                'department_desc': 'fob - field operations bureau',
                'prev_department_code': '193',
                'prev_department_desc': 'Gang Investigation Division',
                'date': str(date(2017, 8, 12)),
                'year': 2017,
            },
            {
                'kind': UNIT_CHANGE_TIMELINE_KIND,
                'department_code': '610',
                'department_desc': 'Detective Area - Central',
                'prev_department_code': None,
                'prev_department_desc': 'fob - field operations bureau',
                'date': str(date(2019, 3, 7)),
                'year': 2019,
            },
            {
                'kind': UNIT_CHANGE_TIMELINE_KIND,
                'department_code': '5020',
                'department_desc': 'police-uniform patrol bureau',
                'prev_department_code': '610',
                'prev_department_desc': 'Detective Area - Central',
                'date': None,
                'year': 2019,
            },
            {
                'kind': UNIT_CHANGE_TIMELINE_KIND,
                'department_code': '5020',
                'department_desc': 'police-uniform patrol bureau',
                'prev_department_code': None,
                'prev_department_desc': None,
                'date': None,
                'year': None,
            },
            {
                'kind': UNIT_CHANGE_TIMELINE_KIND,
                'department_code': '610',
                'department_desc': 'Detective Area - Central',
                'prev_department_code': None,
                'prev_department_desc': None,
                'date': None,
                'year': None,
            },
            {
                'kind': UNIT_CHANGE_TIMELINE_KIND,
                'department_code': None,
                'department_desc': 'msb - management service bureau',
                'prev_department_code': None,
                'prev_department_desc': None,
                'date': None,
                'year': None,
            },
        ]

        assert OfficerTimelineQuery(officer).query() == expected_result
