from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):  # noqa
        return Response({
            'service': settings.SERVICE_NAME,
            'health_status': 1,
        })
