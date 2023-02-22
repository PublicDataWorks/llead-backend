from rest_framework import status, views
from rest_framework.response import Response

from schemas.tasks import validate_schemas


class SchemaView(views.APIView):
    def post(self, request):
        validate_schemas()

        return Response(status=status.HTTP_200_OK)
