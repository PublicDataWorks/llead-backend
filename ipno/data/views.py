from django.conf import settings
from django.core.cache import cache

from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
from rest_framework.views import APIView

from data.constants import IMPORT_TASK_ID_CACHE_KEY
from data.tasks import import_data


class ImportDataView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        x_api_key = request.META.get("HTTP_X_API_KEY")
        if x_api_key != settings.IPNO_API_KEY:
            return Response({"error": "Invalid API Key"}, status=HTTP_403_FORBIDDEN)

        folder_name = request.data.get("folder_name")
        if not folder_name:
            return Response(
                {"error": "Folder name is required"}, status=HTTP_400_BAD_REQUEST
            )

        if cache.get(IMPORT_TASK_ID_CACHE_KEY):
            return Response(
                {"error": "Cannot schedule request, there's another task scheduled"},
                status=HTTP_422_UNPROCESSABLE_ENTITY,
            )

        task = import_data.delay(folder_name)
        cache.set(IMPORT_TASK_ID_CACHE_KEY, task.id)
        return Response({"message": "Request received"}, status=HTTP_200_OK)
