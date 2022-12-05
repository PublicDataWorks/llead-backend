from django.test import TestCase

from app_config.factories import FrontPageCardFactory
from app_config.serializers import FrontPageCardSerializer


class FrontPageCardsSerializerTestCase(TestCase):
    def test_data(self):
        item = FrontPageCardFactory(content="TEST", order=1)

        result = FrontPageCardSerializer(item).data
        assert result == {
            "content": "TEST",
        }
