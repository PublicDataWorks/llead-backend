from io import StringIO, BytesIO
from csv import DictWriter

from django.test.testcases import TestCase, override_settings

from mock import patch, Mock, call

from data.services import OfficerImporter
from data.models import ImportLog
from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.factories import WrglRepoFactory
from officers.models import Officer
from officers.factories import OfficerFactory


class OfficerImporterTestCase(TestCase):
    def setUp(self):
        csv_content = StringIO()
        writer = DictWriter(
            csv_content,
            fieldnames=[
                'uid',
                'last_name',
                'middle_name',
                'middle_initial',
                'first_name',
                'birth_year',
                'birth_month',
                'birth_day',
                'race',
                'gender',
            ]
        )
        self.officers_data = [
            {
                'uid': 'uid1',
                'last_name': 'Sanchez',
                'middle_name': 'C',
                'middle_initial': 'C',
                'first_name': 'Emile',
                'birth_year': '1938',
                'birth_month': '',
                'birth_day': '',
                'race': 'white',
                'gender': 'male',
            },
            {
                'uid': 'uid2',
                'last_name': 'Monaco',
                'middle_name': 'P',
                'middle_initial': 'P',
                'first_name': 'Anthony',
                'birth_year': '1964',
                'birth_month': '12',
                'birth_day': '4',
                'race': 'black / african american',
                'gender': 'female',
            },
            {
                'uid': 'uid3',
                'last_name': 'Maier',
                'middle_name': '',
                'middle_initial': '',
                'first_name': 'Joel',
                'birth_year': '',
                'birth_month': '',
                'birth_day': '',
                'race': '',
                'gender': '',
            },
            {
                'uid': 'uid4',
                'last_name': 'Poindexter',
                'middle_name': 'A',
                'middle_initial': 'A',
                'first_name': 'Sylvia',
                'birth_year': '1973',
                'birth_month': '',
                'birth_day': '',
                'race': '',
                'gender': 'male',
            },
            {
                'uid': 'uid5',
                'last_name': 'Bull',
                'middle_name': '',
                'middle_initial': '',
                'first_name': 'Edward',
                'birth_year': '',
                'birth_month': '',
                'birth_day': '',
                'race': '',
                'gender': 'male',
            },
            {
                'uid': 'uid5',
                'last_name': 'Bull',
                'middle_name': '',
                'middle_initial': '',
                'first_name': 'Edward',
                'birth_year': '',
                'birth_month': '',
                'birth_day': '',
                'race': '',
                'gender': 'male',
            },
        ]
        writer.writeheader()
        writer.writerows(self.officers_data)
        self.csv_stream = BytesIO(csv_content.getvalue().encode('utf-8'))
        self.csv_text = csv_content.getvalue()

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    @patch('data.services.base_importer.requests.get')
    def test_process_successfully(self, get_mock):
        OfficerFactory(uid='uid1')
        OfficerFactory(uid='uid2')
        OfficerFactory(uid='uid3')
        OfficerFactory(uid='uid6')

        assert Officer.objects.count() == 4

        WrglRepoFactory(
            data_model=OfficerImporter.data_model,
            repo_name='officer_repo',
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

        OfficerImporter().process()

        import_log = ImportLog.objects.order_by('-created_at').last()
        assert import_log.data_model == OfficerImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 3
        assert import_log.deleted_rows == 1
        assert not import_log.error_message
        assert import_log.finished_at

        assert Officer.objects.count() == 5

        assert get_mock.call_args_list[0] == call(
            'https://www.wrgl.co/api/v1/users/wrgl_user/repos/officer_repo',
            headers={'Authorization': 'APIKEY wrgl-api-key'},
        )

        for officer_data in self.officers_data:
            officer = Officer.objects.filter(uid=officer_data['uid']).first()
            assert officer
            field_attrs = [
                'last_name',
                'middle_name',
                'middle_initial',
                'first_name',
                'race',
                'gender',
            ]
            integer_field_attrs = [
                'birth_year',
                'birth_month',
                'birth_day',
            ]

            for attr in field_attrs:
                assert getattr(officer, attr) == (officer_data[attr] if officer_data[attr] else None)

            for attr in integer_field_attrs:
                assert getattr(officer, attr) == (int(officer_data[attr]) if officer_data[attr] else None)
