from django.conf import settings
from django.http import FileResponse

from rest_framework import status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from schemas.tasks import validate_schemas
from utils.google_cloud import GoogleCloudService


class SchemaView(views.APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated()]
        return super().get_permissions()

    def post(self, request):
        validate_schemas()

        return Response(status=status.HTTP_200_OK)

    def get(self, request):
        gs = GoogleCloudService()
        gs.download_schema(f"{settings.ENVIRONMENT}-schema.sql")

        return FileResponse(open("schema.sql", "rb"), as_attachment=True)
