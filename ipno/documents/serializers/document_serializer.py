from rest_framework import serializers

from shared.serializers import SimpleDepartmentSerializer


class DocumentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    document_type = serializers.CharField()
    title = serializers.CharField()
    url = serializers.CharField()
    preview_image_url = serializers.CharField()
    incident_date = serializers.DateField()
    pages_count = serializers.IntegerField()

    departments = serializers.SerializerMethodField()

    def get_departments(self, obj):
        departments = set()
        for officer in obj.officers.all():
            for officer_history in officer.prefetched_officer_histories:
                departments.add(officer_history.department)

        return SimpleDepartmentSerializer(departments, many=True).data
