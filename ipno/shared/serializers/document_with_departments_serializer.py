from rest_framework import serializers

from shared.serializers import SimpleDepartmentSerializer


class DocumentWithDepartmentsSerializer(serializers.Serializer):
    departments = serializers.SerializerMethodField()

    def get_departments(self, obj):
        departments = set(obj.departments.all())
        for officer in obj.officers.all():
            for officer_history in officer.prefetched_officer_histories:
                departments.add(officer_history.department)

        return SimpleDepartmentSerializer(departments, many=True).data
