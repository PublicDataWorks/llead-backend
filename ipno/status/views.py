from rest_framework.response import Response
from rest_framework import status, views


class StatusView(views.APIView):
    def get(self, request):
        return Response(status=status.HTTP_200_OK)
