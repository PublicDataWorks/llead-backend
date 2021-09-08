from io import StringIO, BytesIO
from csv import DictWriter

from django.test.testcases import TestCase, override_settings

from mock import patch, Mock, call

from data.services import UofImporter
from data.models import ImportLog
from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.factories import WrglRepoFactory
from use_of_forces.models import UseOfForce
from use_of_forces.factories import UseOfForceFactory
from officers.factories import OfficerFactory
from departments.factories import DepartmentFactory


class UofImporterTestCase(TestCase):
    def setUp(self):
        csv_content = StringIO()
        writer = DictWriter(
            csv_content,
            fieldnames=[
                'uid',
                'agency',
                'uof_uid',
                'uof_tracking_number',
                'report_year',
                'force_description',
                'force_type',
                'force_level',
                'effective_uof',
                'accidental_discharge',
                'less_than_lethal',
                'status',
                'source',
                'service_type',
                'county',
                'traffic_stop',
                'sustained',
                'force_reason',
                'weather_description',
                'distance_from_officer',
                'body_worn_camera_available',
                'app_used',
                'citizen_uid',
                'citizen_arrested',
                'citizen_hospitalized',
                'citizen_injured',
                'citizen_body_type',
                'citizen_height',
                'citizen_age',
                'citizen_involvement',
                'disposition',
                'citizen_sex',
                'citizen_race',
                'citizen_age_1',
                'officer_current_supervisor',
                'officer_title',
                'officer_injured',
                'officer_age',
                'officer_years_exp',
                'officer_years_with_unit',
                'officer_type',
                'officer_employment_status',
                'officer_department',
                'officer_division',
                'officer_sub_division_a',
                'officer_sub_division_b',
                'data_production_year',
            ]
        )
        self.uof1_data = {
            'uof_uid': 'uof-uid1',
            'uof_tracking_number': 'FTN2015-0705',
            'report_year': '2015',
            'uid': 'officer-uid1',
            'force_description': 'L2-CEW Deployment',
            'force_type': 'L2-Taser',
            'force_level': 'L2',
            'effective_uof': 'yes',
            'accidental_discharge': 'no',
            'less_than_lethal': 'yes',
            'status': 'Completed',
            'source': 'source',
            'service_type': 'Pedestrian Stop',
            'county': 'Orleans Parish',
            'traffic_stop': 'no',
            'sustained': 'no',
            'force_reason': 'resisting lawful arrest',
            'weather_description': 'clear conditions',
            'distance_from_officer': '4 feet to 6 feet',
            'body_worn_camera_available': 'yes',
            'app_used': 'blueteam',
            'citizen_uid': 'citizen-uid-1',
            'citizen_arrested': 'yes',
            'citizen_hospitalized': 'no',
            'citizen_injured': 'no',
            'citizen_body_type': 'medium',
            'citizen_height': "5'10'' to 6'0''",
            'citizen_age': '24',
            'citizen_involvement': 'complainant',
            'disposition': 'Authorized',
            'citizen_sex': 'male',
            'citizen_race': 'black',
            'citizen_age_1': '25',
            'officer_current_supervisor': '821',
            'officer_title': 'senior police officer',
            'officer_injured': 'no',
            'officer_age': '27',
            'officer_years_exp': '6',
            'officer_years_with_unit': '3',
            'officer_type': 'commissioned',
            'officer_employment_status': 'active',
            'officer_department': 'ISB - Investigations and Support Bureau',
            'officer_division': 'Special Investigations Division',
            'officer_sub_division_a': 'Street Gang Unit',
            'officer_sub_division_b': 'Squad A',
            'agency': 'New Orleans PD',
            'data_production_year': '2019'
        }
        self.uof2_data = {
            'uof_uid': 'uof-uid2',
            'uof_tracking_number': 'FTN2015-0710',
            'report_year': '2015',
            'uid': 'officer-uid-invalid',
            'force_description': 'L1-Hands',
            'force_type': 'Hands / Escort tech',
            'force_level': 'L1',
            'effective_uof': 'yes',
            'accidental_discharge': '',
            'less_than_lethal': '',
            'status': 'Completed',
            'source': '',
            'service_type': 'Call for Service',
            'county': 'Orleans Parish',
            'traffic_stop': 'no',
            'sustained': 'no',
            'force_reason': 'refuse verbal commands',
            'weather_description': 'clear conditions',
            'distance_from_officer': '0 feet to 1 feet',
            'body_worn_camera_available': 'yes',
            'app_used': 'blueteam',
            'citizen_uid': 'citizen-uid-2',
            'citizen_arrested': 'no',
            'citizen_hospitalized': 'no',
            'citizen_injured': 'no',
            'citizen_body_type': 'large',
            'citizen_height': "> 6'3''",
            'citizen_age': '48',
            'citizen_involvement': 'complainant',
            'disposition': 'Authorized',
            'citizen_sex': 'male',
            'citizen_race': 'black',
            'citizen_age_1': '48',
            'officer_current_supervisor': '',
            'officer_title': 'senior police officer',
            'officer_injured': 'no',
            'officer_age': '42',
            'officer_years_exp': '14',
            'officer_years_with_unit': '4',
            'officer_type': 'commissioned',
            'officer_employment_status': 'active',
            'officer_department': 'FOB - Field Operations Bureau',
            'officer_division': 'Second District',
            'officer_sub_division_a': 'C Platoon',
            'officer_sub_division_b': '',
            'agency': '',
            'data_production_year': '2019'
        }
        self.uof3_data = {
            'uof_uid': 'uof-uid3',
            'uof_tracking_number': 'FTN2015-0713',
            'report_year': '2015',
            'uid': 'officer-uid2',
            'force_description': 'L1-Firearm (Exhibited)',
            'force_type': 'Firearm Exhibited',
            'force_level': 'L1',
            'effective_uof': 'yes',
            'accidental_discharge': '',
            'less_than_lethal': '',
            'status': 'Completed',
            'source': '',
            'service_type': 'Serving a Warrant',
            'county': 'Orleans Parish',
            'traffic_stop': 'no',
            'sustained': 'no',
            'force_reason': 'other',
            'weather_description': 'clear conditions',
            'distance_from_officer': '1 feet to 3 feet',
            'body_worn_camera_available': 'yes',
            'app_used': 'blueteam',
            'citizen_uid': 'citizen-uid-3',
            'citizen_arrested': 'yes',
            'citizen_hospitalized': 'no',
            'citizen_injured': 'no',
            'citizen_body_type': 'small',
            'citizen_height': "5'7'' to 5'9''",
            'citizen_age': '35',
            'citizen_involvement': 'complainant',
            'disposition': 'Authorized',
            'citizen_sex': 'female',
            'citizen_race': 'black',
            'citizen_age_1': '35',
            'officer_current_supervisor': '3585',
            'officer_title': 'senior police officer',
            'officer_injured': 'no',
            'officer_age': '29',
            'officer_years_exp': '8',
            'officer_years_with_unit': '4',
            'officer_type': 'commissioned',
            'officer_employment_status': 'active',
            'officer_department': 'FOB - Field Operations Bureau',
            'officer_division': 'Special Operations Division',
            'officer_sub_division_a': 'Tactical Section',
            'officer_sub_division_b': 'Admin Unit',
            'agency': 'Baton Rouge PD',
            'data_production_year': '2019'
        }
        self.uof4_data = {
            'uof_uid': 'uof-uid4',
            'uof_tracking_number': 'FTN2015-0735',
            'report_year': '2015',
            'uid': '',
            'force_description': 'L1-Firearm (Exhibited)',
            'force_type': 'Firearm Exhibited',
            'force_level': 'L1',
            'effective_uof': 'yes',
            'accidental_discharge': '',
            'less_than_lethal': '',
            'status': 'Completed',
            'source': '',
            'service_type': 'Serving a Warrant',
            'county': 'Orleans Parish',
            'traffic_stop': 'no',
            'sustained': 'no',
            'force_reason': 'other',
            'weather_description': 'rainy conditions - medium',
            'distance_from_officer': '11 feet to 14 feet',
            'body_worn_camera_available': 'yes',
            'app_used': 'blueteam',
            'citizen_uid': 'citizen-uid-4',
            'citizen_arrested': 'no',
            'citizen_hospitalized': 'no',
            'citizen_injured': 'no',
            'citizen_body_type': 'medium',
            'citizen_height': "5'7'' to 5'9''",
            'citizen_age': '14',
            'citizen_involvement': 'complainant',
            'disposition': 'Authorized',
            'citizen_sex': 'female',
            'citizen_race': 'black',
            'citizen_age_1': '14',
            'officer_current_supervisor': '3682',
            'officer_title': 'senior police officer',
            'officer_injured': 'no',
            'officer_age': '32',
            'officer_years_exp': '10',
            'officer_years_with_unit': '2',
            'officer_type': 'commissioned',
            'officer_employment_status': 'active',
            'officer_department': 'FOB - Field Operations Bureau',
            'officer_division': 'Special Operations Division',
            'officer_sub_division_a': 'Tactical Section',
            'officer_sub_division_b': 'Armory Unit',
            'agency': 'New Orleans PD',
            'data_production_year': '2019'
        }
        self.uof5_data = {
            'uof_uid': 'uof-uid5',
            'uof_tracking_number': 'FTN2016-0026',
            'report_year': '2016',
            'uid': 'officer-uid3',
            'force_description': 'L1-Firearm (Exhibited)',
            'force_type': 'Firearm Exhibited',
            'force_level': 'L1',
            'effective_uof': 'yes',
            'accidental_discharge': '',
            'less_than_lethal': '',
            'status': 'Completed',
            'source': '',
            'service_type': 'Call for Service',
            'county': 'Orleans Parish',
            'traffic_stop': 'no',
            'sustained': 'no',
            'force_reason': 'other',
            'weather_description': 'clear conditions',
            'distance_from_officer': '11 feet to 14 feet',
            'body_worn_camera_available': 'yes',
            'app_used': 'blueteam',
            'citizen_uid': 'citizen-uid-5',
            'citizen_arrested': 'yes',
            'citizen_hospitalized': 'no',
            'citizen_injured': 'no',
            'citizen_body_type': 'medium',
            'citizen_height': "5'7'' to 5'9''",
            'citizen_age': '36',
            'citizen_involvement': 'complainant',
            'disposition': 'Authorized',
            'citizen_sex': 'male',
            'citizen_race': 'black',
            'citizen_age_1': '37',
            'officer_current_supervisor': '3571',
            'officer_title': 'senior police officer',
            'officer_injured': 'no',
            'officer_age': '29',
            'officer_years_exp': '2',
            'officer_years_with_unit': '1',
            'officer_type': 'non-commisioned',
            'officer_employment_status': 'active',
            'officer_department': 'FOB - Field Operations Bureau',
            'officer_division': 'Eighth District',
            'officer_sub_division_a': 'Narcotics',
            'officer_sub_division_b': '',
            'agency': 'Baton Rouge PD',
            'data_production_year': '2019'
        }
        self.uofs_data = [
            self.uof1_data,
            self.uof2_data,
            self.uof3_data,
            self.uof4_data,
            self.uof5_data,
            self.uof5_data,
        ]
        writer.writeheader()
        writer.writerows(self.uofs_data)
        self.csv_stream = BytesIO(csv_content.getvalue().encode('utf-8'))
        self.csv_text = csv_content.getvalue()

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    @patch('data.services.base_importer.requests.get')
    def test_process_successfully(self, get_mock):
        UseOfForceFactory(uof_uid='uof-uid1')
        UseOfForceFactory(uof_uid='uof-uid2')
        UseOfForceFactory(uof_uid='uof-uid3')
        UseOfForceFactory(uof_uid='uof-uid6')

        department_1 = DepartmentFactory(name='New Orleans PD')
        department_2 = DepartmentFactory(name='Baton Rouge PD')

        officer_1 = OfficerFactory(uid='officer-uid1')
        officer_2 = OfficerFactory(uid='officer-uid2')
        officer_3 = OfficerFactory(uid='officer-uid3')

        assert UseOfForce.objects.count() == 4

        WrglRepoFactory(
            data_model=UofImporter.data_model,
            repo_name='uof_repo',
            commit_hash='bf56dded0b1c4b57f425acb75d48e68c'
        )

        data = {
            'hash': '3950bd17edfd805972781ef9fe2c6449'
        }
        mock_json = Mock(return_value=data)
        get_mock.return_value = Mock(
            json=mock_json,
            text=self.csv_text,
        )

        UofImporter().process()

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == UofImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 3
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert UseOfForce.objects.count() == 5

        assert get_mock.call_args_list[0] == call(
            'https://www.wrgl.co/api/v1/users/wrgl_user/repos/uof_repo',
            headers={'Authorization': 'APIKEY wrgl-api-key'},
        )

        expected_uof1_data = self.uof1_data.copy()
        expected_uof1_data['department_id'] = department_1.id
        expected_uof1_data['officer_id'] = officer_1.id

        expected_uof2_data = self.uof2_data.copy()
        expected_uof2_data['department_id'] = None
        expected_uof2_data['officer_id'] = None

        expected_uof3_data = self.uof3_data.copy()
        expected_uof3_data['department_id'] = department_2.id
        expected_uof3_data['officer_id'] = officer_2.id

        expected_uof4_data = self.uof4_data.copy()
        expected_uof4_data['department_id'] = department_1.id
        expected_uof4_data['officer_id'] = None

        expected_uof5_data = self.uof5_data.copy()
        expected_uof5_data['department_id'] = department_2.id
        expected_uof5_data['officer_id'] = officer_3.id

        expected_uofs_data = [
            expected_uof1_data,
            expected_uof2_data,
            expected_uof3_data,
            expected_uof4_data,
            expected_uof5_data,
        ]

        for uof_data in expected_uofs_data:
            uof = UseOfForce.objects.filter(uof_uid=uof_data['uof_uid']).first()
            assert uof
            field_attrs = [
                'department_id',
                'officer_id',
                'uof_uid',
                'uof_tracking_number',
                'force_description',
                'force_type',
                'force_level',
                'effective_uof',
                'accidental_discharge',
                'less_than_lethal',
                'status',
                'source',
                'service_type',
                'county',
                'traffic_stop',
                'sustained',
                'force_reason',
                'weather_description',
                'distance_from_officer',
                'body_worn_camera_available',
                'app_used',
                'citizen_arrested',
                'citizen_hospitalized',
                'citizen_injured',
                'citizen_body_type',
                'citizen_height',
                'citizen_involvement',
                'disposition',
                'citizen_sex',
                'citizen_race',
                'citizen_age_1',
                'officer_current_supervisor',
                'officer_title',
                'officer_injured',
                'officer_age',
                'officer_type',
                'officer_employment_status',
                'officer_department',
                'officer_division',
                'officer_sub_division_a',
                'officer_sub_division_b',
            ]
            integer_field_attrs = [
                'report_year',
                'citizen_age',
                'officer_years_exp',
                'officer_years_with_unit',
                'data_production_year',
            ]

            for attr in field_attrs:
                assert getattr(uof, attr) == (uof_data[attr] if uof_data[attr] else None)

            for attr in integer_field_attrs:
                assert getattr(uof, attr) == (int(uof_data[attr]) if uof_data[attr] else None)
