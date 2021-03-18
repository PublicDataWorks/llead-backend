from datetime import date
from django.test.testcases import TestCase

from departments.factories import DepartmentFactory
from officers.factories import OfficerFactory, OfficerHistoryFactory
from documents.factories import DocumentFactory
from complaints.factories import ComplaintFactory


class DepartmentTestCase(TestCase):
    def test_documents(self):
        department = DepartmentFactory()

        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        officer_3 = OfficerFactory()

        OfficerHistoryFactory(
            department=department,
            officer=officer_1,
            start_date=date(2018, 2, 3),
            end_date=date(2021, 2, 3),
        )
        OfficerHistoryFactory(
            department=department,
            officer=officer_2,
            start_date=date(2018, 4, 5),
            end_date=date(2019, 4, 5),
        )
        OfficerHistoryFactory(
            department=department,
            officer=officer_3,
            start_date=date(2018, 4, 5),
            end_date=date(2019, 4, 5),
        )

        document_1 = DocumentFactory(incident_date=date(2020, 5, 4))
        document_2 = DocumentFactory(incident_date=date(2017, 12, 5))
        document_3 = DocumentFactory(incident_date=date(2019, 11, 6))
        document_4 = DocumentFactory(incident_date=date(2018, 8, 9))
        document_5 = DocumentFactory(incident_date=date(2018, 8, 9))
        document_6 = DocumentFactory(incident_date=date(2018, 8, 10))
        document_7 = DocumentFactory(incident_date=None)
        document_1.officers.add(officer_1)
        document_2.officers.add(officer_1)
        document_3.officers.add(officer_1)
        document_4.officers.add(officer_3)
        document_5.officers.add(officer_3)
        document_7.officers.add(officer_2, officer_3)
        document_1.departments.add(department)
        document_6.departments.add(department)

        expected_results = {
            document_1,
            document_3,
            document_4,
            document_5,
            document_6,
        }

        assert set(department.documents) == expected_results

    def test_complaints(self):
        department = DepartmentFactory()

        officer_1 = OfficerFactory()
        officer_2 = OfficerFactory()
        officer_3 = OfficerFactory()

        OfficerHistoryFactory(
            department=department,
            officer=officer_1,
            start_date=date(2018, 2, 3),
            end_date=date(2021, 2, 3),
        )
        OfficerHistoryFactory(
            department=department,
            officer=officer_2,
            start_date=date(2018, 4, 5),
            end_date=date(2019, 4, 5),
        )
        OfficerHistoryFactory(
            department=department,
            officer=officer_3,
            start_date=date(2018, 4, 5),
            end_date=date(2019, 4, 5),
        )

        complaint_1 = ComplaintFactory(incident_date=date(2020, 5, 4))
        complaint_2 = ComplaintFactory(incident_date=date(2017, 12, 5))
        complaint_3 = ComplaintFactory(incident_date=date(2019, 11, 6))
        complaint_4 = ComplaintFactory(incident_date=date(2018, 8, 9))
        complaint_5 = ComplaintFactory(incident_date=date(2018, 8, 9))
        complaint_6 = ComplaintFactory(incident_date=None)
        complaint_7 = ComplaintFactory(incident_date=None)
        complaint_8 = ComplaintFactory(incident_date=None)
        complaint_1.officers.add(officer_1)
        complaint_2.officers.add(officer_1)
        complaint_3.officers.add(officer_1)
        complaint_4.officers.add(officer_3)
        complaint_6.officers.add(officer_2, officer_3)
        complaint_7.departments.add(department)
        complaint_8.departments.add(department)
        complaint_1.departments.add(department)
        complaint_5.departments.add(department)

        expected_results = {
            complaint_1,
            complaint_3,
            complaint_4,
            complaint_5,
            complaint_7,
            complaint_8,
        }

        assert set(department.complaints) == expected_results

    def test_document_years(self):
        department = DepartmentFactory()

        document_1 = DocumentFactory(incident_date=date(2016, 5, 4))
        document_2 = DocumentFactory(incident_date=date(2019, 5, 4))
        document_3 = DocumentFactory(incident_date=date(2018, 5, 4))

        document_1.departments.add(department)
        document_2.departments.add(department)
        document_3.departments.add(department)

        assert sorted(department.document_years) == [2016, 2018, 2019]

    def test_complaint_years(self):
        department = DepartmentFactory()

        complaint_1 = ComplaintFactory(incident_date=date(2012, 5, 4))
        complaint_2 = ComplaintFactory(incident_date=date(2020, 5, 4))
        complaint_3 = ComplaintFactory(incident_date=date(2018, 5, 4))

        complaint_1.departments.add(department)
        complaint_2.departments.add(department)
        complaint_3.departments.add(department)

        assert sorted(department.complaint_years) == [2012, 2018, 2020]
