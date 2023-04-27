from rest_framework import status, views
from rest_framework.response import Response

from findings.models import Finding
from findings.serializers.finding_serializer import FindingSerializer


class FindingView(views.APIView):
    def get(self, request):
        finding = Finding.objects.all().first()

        serializer = FindingSerializer(finding, context={"request": request})

        return Response(serializer.data, status=status.HTTP_200_OK)
