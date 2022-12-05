from django.test.testcases import TestCase

from mock import patch

from utils.search_index import rebuild_search_index


class SearchIndexTestCase(TestCase):
    @patch("documents.documents.DocumentESDoc.rebuild_index")
    @patch("officers.documents.OfficerESDoc.rebuild_index")
    @patch("departments.documents.DepartmentESDoc.rebuild_index")
    def test_rebuild_search_index(
        self,
        department_rebuild_index,
        officer_rebuild_index,
        document_rebuild_index,
    ):
        rebuild_search_index()

        department_rebuild_index.assert_called()
        officer_rebuild_index.assert_called()
        document_rebuild_index.assert_called()
