from django.conf import settings
from django.http import FileResponse

from rest_framework import views
from rest_framework.permissions import IsAuthenticated

from utils.google_cloud import GoogleCloudService


class SchemaView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        gs = GoogleCloudService(settings.SCHEMA_BUCKET_NAME)
        gs.download_schema(f"{settings.ENVIRONMENT}-schema.sql")

        return FileResponse(open("schema.sql", "rb"), as_attachment=True)
