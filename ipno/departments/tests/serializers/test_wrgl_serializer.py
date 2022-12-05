from django.test import TestCase

from departments.factories import WrglFileFactory
from departments.serializers import WrglFileSerializer


class WrglFileSerializerTestCase(TestCase):
    def test_data(self):
        wrgl_file = WrglFileFactory()

        result = WrglFileSerializer(wrgl_file).data
        assert result == {
            "id": wrgl_file.id,
            "name": wrgl_file.name,
            "slug": wrgl_file.slug,
            "description": wrgl_file.description,
            "url": wrgl_file.url,
            "download_url": wrgl_file.download_url,
            "default_expanded": wrgl_file.default_expanded,
        }
