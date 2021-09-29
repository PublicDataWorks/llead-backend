from django.test import TestCase

from app_config.factories import FrontPageOrderFactory
from app_config.serializers import FrontPageOrderSerializer


class FrontPageOrdersSerializerTestCase(TestCase):
    def test_data(self):
        item = FrontPageOrderFactory(section='TEST', order=1)

        result = FrontPageOrderSerializer(item).data
        assert result == {
            'section': 'TEST',
            'order': 1
        }
