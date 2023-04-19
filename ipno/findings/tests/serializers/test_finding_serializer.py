from django.test import TestCase

from findings.factories import FindingFactory
from findings.serializers.finding_serializer import FindingSerializer


class FindingSerializerTestCase(TestCase):
    def test_data(self):
        findings = FindingFactory()

        result = FindingSerializer(findings).data

        assert result == {
            "background_image_url": None,
            "title": findings.title,
            "description": findings.description,
            "card_image_url": None,
            "card_title": findings.card_title,
            "card_author": findings.card_author,
            "card_department": findings.card_department,
        }
