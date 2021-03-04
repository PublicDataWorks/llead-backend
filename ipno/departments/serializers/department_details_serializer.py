from rest_framework import serializers


class WrglFileSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()
    description = serializers.CharField()
    url = serializers.CharField()
    download_url = serializers.CharField()
    default_expanded = serializers.BooleanField()


class DepartmentDetailsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
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
        return obj.officers.count()

    def get_complaints_count(self, obj):
        return obj.complaints.count()

    def get_documents_count(self, obj):
        return obj.documents.count()

    def get_wrgl_files(self, obj):
        return WrglFileSerializer(obj.wrglfile_set.order_by('position'), many=True).data

    def get_data_period(self, obj):
        years = obj.officerhistory_set.filter(
            start_date__isnull=False,
            end_date__isnull=False
        ).order_by('start_date__year').values_list('start_date__year', 'end_date__year')

        data_period = []
        current_start_year = None
        current_end_year = None
        for start_year, end_year in years:
            if current_start_year is None:
                current_start_year = start_year
                current_end_year = end_year
            elif start_year <= current_end_year:
                current_end_year = end_year
            else:
                data_period.append([current_start_year, current_end_year])
                current_start_year = start_year
                current_end_year = end_year

        if current_start_year:
            data_period.append([current_start_year, current_end_year])

        return [
            f'{start_year}{f"-{end_year}" if start_year != end_year else ""}'
            for start_year, end_year in data_period
        ]
