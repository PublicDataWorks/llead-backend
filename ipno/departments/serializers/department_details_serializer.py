from rest_framework import serializers

from utils.data_utils import data_period


class WrglFileSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()
    description = serializers.CharField()
    url = serializers.CharField()
    download_url = serializers.CharField()
    default_expanded = serializers.BooleanField()


class DepartmentDetailsSerializer(serializers.Serializer):
    id = serializers.CharField(source='slug')
    name = serializers.CharField()
    city = serializers.CharField()
    parish = serializers.CharField()
    location_map_url = serializers.CharField()

    officers_count = serializers.SerializerMethodField()
    complaints_count = serializers.SerializerMethodField()
    documents_count = serializers.SerializerMethodField()
    wrgl_files = serializers.SerializerMethodField()
    data_period = serializers.SerializerMethodField()

    def get_officers_count(self, obj):
        return obj.officers.distinct().count()

    def get_complaints_count(self, obj):
        return obj.complaints.count()

    def get_documents_count(self, obj):
        return obj.documents.count()

    def get_wrgl_files(self, obj):
        return WrglFileSerializer(obj.wrgl_files.order_by('position'), many=True).data

    def get_data_period(self, obj):
        event_years = list(obj.events.filter(
            year__isnull=False,
        ).values_list('year', flat=True))
        years = event_years + obj.document_years

        return data_period(years)
