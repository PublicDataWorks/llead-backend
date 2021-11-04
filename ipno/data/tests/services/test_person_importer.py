from io import StringIO, BytesIO
from csv import DictWriter

from django.test.testcases import TestCase, override_settings

from mock import patch, Mock, call

from data.services import PersonImporter
from data.models import ImportLog
from data.constants import IMPORT_LOG_STATUS_FINISHED
from data.factories import WrglRepoFactory
from officers.factories import OfficerFactory
from people.factories import PersonFactory
from people.models import Person


class PersonImporterTestCase(TestCase):
    def setUp(self):
        csv_content = StringIO()
        writer = DictWriter(
            csv_content,
            fieldnames=[
                'person_id',
                'canonical_uid',
                'uids',
            ]
        )
        self.person1_data = {
            'person_id': '1',
            'canonical_uid': '000526fa05739e97b61343513a92dbc7',
            'uids': '000526fa05739e97b61343513a92dbc7',
        }
        self.person2_data = {
            'person_id': '2',
            'canonical_uid': '0005624eee7c188d3604f2294dfb195d',
            'uids': '0005624eee7c188d3604f2294dfb195d,0007884f101d1661937abb130664d2d2',
        }
        self.person3_data = {
            'person_id': '3',
            'canonical_uid': '0007f3f6802b9fa493622d4a23edc00b',
            'uids': '0007f3f6802b9fa493622d4a23edc00b,0019ddf9abe0273e2d57215ec51697a1',
        }
        self.person4_data = {
            'person_id': '3',
            'canonical_uid': '0007f3f6802b9fa2d4a23edc00b',
            'uids': '0007f3f6802b9fa2d4a23edc00b',
        }
        self.people_data = [
            self.person1_data,
            self.person2_data,
            self.person3_data,
            self.person4_data,
        ]
        writer.writeheader()
        writer.writerows(self.people_data)
        self.csv_stream = BytesIO(csv_content.getvalue().encode('utf-8'))
        self.csv_text = csv_content.getvalue()

        self.officer1 = OfficerFactory(uid='000526fa05739e97b61343513a92dbc7')
        self.officer2 = OfficerFactory(uid='0005624eee7c188d3604f2294dfb195d')
        self.officer3 = OfficerFactory(uid='0007884f101d1661937abb130664d2d2')
        self.officer4 = OfficerFactory(uid='0007f3f6802b9fa493622d4a23edc00b')

    @override_settings(WRGL_API_KEY='wrgl-api-key')
    @patch('data.services.base_importer.WRGL_USER', 'wrgl_user')
    @patch('data.services.base_importer.requests.get')
    def test_process_successfully(self, get_mock):
        updating_person = PersonFactory()
        updating_person.person_id = '1'
        updating_person.canonical_officer = self.officer4
        updating_person.officers.add(self.officer4)
        updating_person.save()

        WrglRepoFactory(
            data_model=PersonImporter.data_model,
            repo_name='person_repo',
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

        PersonImporter().process()

        import_log = ImportLog.objects.order_by('-created_at').last()

        assert import_log.data_model == PersonImporter.data_model
        assert import_log.status == IMPORT_LOG_STATUS_FINISHED
        assert import_log.commit_hash == '3950bd17edfd805972781ef9fe2c6449'
        assert import_log.created_rows == 2
        assert import_log.updated_rows == 5
        assert import_log.deleted_rows == 0
        assert not import_log.error_message
        assert import_log.finished_at

        assert Person.objects.count() == 3

        results = Person.objects.all()

        assert get_mock.call_args_list[0] == call(
            'https://www.wrgl.co/api/v1/users/wrgl_user/repos/person_repo',
            headers={'Authorization': 'APIKEY wrgl-api-key'},
        )

        expected_person1_data = self.person1_data.copy()
        assert results.first().person_id == expected_person1_data['person_id']
        assert results.first().canonical_officer.uid == expected_person1_data['canonical_uid']
        assert expected_person1_data['uids'] in results.first().officers.values_list('uid', flat=True)

        expected_person2_data = self.person2_data.copy()
        expected_uids_list = results[0].officers.values_list('uid', flat=True)
        assert expected_uids_list.count() == 2
        assert results[0].person_id == expected_person2_data['person_id']
        assert expected_person2_data['uids'].split(',')[0] in expected_uids_list
        assert expected_person2_data['uids'].split(',')[1] in expected_uids_list

        expected_person3_data = self.person3_data.copy()
        assert results.last().person_id == expected_person3_data['person_id']
        assert results.last().canonical_officer.uid == expected_person3_data['canonical_uid']
        expected_uids_list = results.last().officers.values_list('uid', flat=True)
        assert expected_uids_list.count() == 1
        assert expected_person3_data['uids'].split(',')[0] in expected_uids_list
        assert expected_person3_data['uids'].split(',')[1] not in expected_uids_list
