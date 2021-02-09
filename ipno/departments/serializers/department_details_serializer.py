from django.db.models import F, Q

from rest_framework import serializers

from documents.models import Document
from complaints.models import Complaint


class DepartmentDetailsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    city = serializers.CharField()
    parish = serializers.CharField()
    location_map_url = serializers.CharField()

    officers_count = serializers.SerializerMethodField()
    complaints_count = serializers.SerializerMethodField()
    documents_count = serializers.SerializerMethodField()

    @staticmethod
    def filter_by_department(klass, department_id):
        return klass.objects.filter(
            incident_date__isnull=False,
            officers__officerhistory__start_date__isnull=False,
            incident_date__gte=F('officers__officerhistory__start_date'),
            officers__officerhistory__department_id=department_id,
        ).filter(
            Q(officers__officerhistory__end_date__isnull=True) |
            Q(incident_date__lte=F('officers__officerhistory__end_date')),
        )

    def get_officers_count(self, obj):
        return obj.officers.count()

    def get_complaints_count(self, obj):
        return self.filter_by_department(
            Complaint, obj.id
        ).count()

    def get_documents_count(self, obj):
        return self.filter_by_department(
            Document, obj.id
        ).count()
