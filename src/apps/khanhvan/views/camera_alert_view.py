import logging
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common import drf
from common.drf import PageNumberPagination


# Vannhk

from ..serializers import camera_serializer

from ..selectors import camera_alert_selector as selector
from ..serializers import camera_alert_serializer
logger = logging.getLogger('app')
DEFAULT_CAPTURE_TIME = 0


class CameraFilterSerializer(serializers.Serializer):

    camera_id = serializers.IntegerField(required=False)
    camera_name = serializers.CharField(required=False)

    type = serializers.CharField(required=False)
    desc = serializers.CharField(required=False)


class CameraAlertListView(APIView):
    InputSerializer = camera_serializer.CameraInputSerializer

    class FilterDeleteSerializer(serializers.Serializer):
        cameras = serializers.ListField(
            child=serializers.IntegerField(min_value=0)
        )

    def get(self, request):

        filter_serializer = CameraFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        validated_data = filter_serializer.validated_data

        logger.info(f" =============== Camera filter: {validated_data} ======================")
        # get list of cameras
        camera_alerts, output_serializer_class = selector.get_list_camera_alerts(validated_data, user=request.user)


        if validated_data.get('all'):
            return Response({
                "results": output_serializer_class(camera_alerts, many=True).data
            })

        return drf.get_paginated_response( # phan trang
            pagination_class = drf.PageNumberPagination,
            serializer_class = output_serializer_class,
            queryset = camera_alerts,
            request = request,
            view = self
        )


class CameraAlertDetailView(APIView):

    def get(self, request, pk): # noqa
        camera_alert, output_serializer_class = selector.get_camera_alert_detail(pk, user=request.user)
        if not camera_alert:
            return Response({"error": "Camera Alert not found"}, status=status.HTTP_404_NOT_FOUND)

        logger.info(camera_alert)
        return Response(output_serializer_class(camera_alert).data)


