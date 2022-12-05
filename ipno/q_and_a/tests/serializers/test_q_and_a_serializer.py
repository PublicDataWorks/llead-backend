from django.test import TestCase

from q_and_a.factories import QuestionFactory, SectionFactory
from q_and_a.serializers import QAndASerializer


class QAndASerializerTestCase(TestCase):
    def test_data(self):
        section = SectionFactory()
        question = QuestionFactory(section=section)

        result = QAndASerializer(section).data
        assert result == {
            "section": section.name,
            "q_and_a": [
                {
                    "question": question.question,
                    "answer": question.answer,
                }
            ],
        }
