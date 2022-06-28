from rest_framework import serializers


class QAndASerializer(serializers.Serializer):
    section = serializers.CharField(source='name')
    q_and_a = serializers.SerializerMethodField()

    def get_q_and_a(self, obj):
        q_and_a = [{'question': o.question, 'answer': o.answer} for o in obj.questions.all()]

        return q_and_a
