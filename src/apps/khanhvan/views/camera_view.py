import datetime
import logging

from django.core.validators import URLValidator
from django.db.utils import IntegrityError

from django.utils import timezone

from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common import drf
from common.drf import PageNumberPagination
from common.exceptions import ApplicationError

# Vannhk
from ..selectors import camera_selector as selector
from ..serializers import camera_serializer
from ..services import camera_service as service
from ..services.snapshot import capture_camera_snapshot

logger = logging.getLogger('app')
DEFAULT_CAPTURE_TIME = 0


class CameraFilterSerializer(serializers.Serializer):
    sort = serializers.CharField(required=False)
    all = serializers.BooleanField(required=False)
    return_mode = serializers.CharField(default='all')  # simple, live, location, all (default)

    cameras = serializers.ListField(child=serializers.IntegerField(), required=False)
    name = serializers.CharField(required=False)

    # group
    # find cameras in list of groups
    groups = serializers.ListField(child=serializers.IntegerField(), required=False)
    # find cameras in this group
    group = serializers.IntegerField(required=False)
    # find cameras have group
    has_group = serializers.BooleanField(required=False, allow_null=True, default=None)

    # others
    conn_status = serializers.IntegerField(required=False)


class CameraFilterView(APIView):
    def post(self, request):
        filter_serializer = CameraFilterSerializer(data=request.data)
        filter_serializer.is_valid(raise_exception=True)
        validated_data = filter_serializer.validated_data

        # get list of cameras
        cameras, output_serializer_class = selector.get_list_cameras(validated_data=validated_data, user=request.user)

        if validated_data.get('all'):
            return Response({
                "results": output_serializer_class(cameras, many=True).data
            })

        return drf.get_paginated_response(
            pagination_class=PageNumberPagination,
            serializer_class=output_serializer_class,
            queryset=cameras,
            request=request,
            view=self
        )


class CameraListView(APIView):
    InputSerializer = camera_serializer.CameraInputSerializer

    class FilterDeleteSerializer(serializers.Serializer):
        cameras = serializers.ListField(
            child=serializers.IntegerField(min_value=0)
        )

    def get(self, request):
        filter_serializer = CameraFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        validated_data = filter_serializer.validated_data

        # get list of cameras
        cameras, output_serializer_class = selector.get_list_cameras(validated_data, user=request.user)

        if validated_data.get('all'):
            return Response({
                "results": output_serializer_class(cameras, many=True).data
            })

        return drf.get_paginated_response( # phan trang
            pagination_class = drf.PageNumberPagination,
            serializer_class = output_serializer_class,
            queryset = cameras,
            request = request,
            view = self
        )

 # === viet lai ===
        # return drf.get_paginated_response(  # phan trang
        #     page_size = 5,
        #     page_number = 1,
        #     queryset = cameras,
        #     serializer_class = output_serializer_class,
        # )


    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        try:
            camera = service.create_camera(validated_data, user=request.user)
        except IntegrityError as ex:
            logger.error('Failed to create camera %s', ex)
            raise ApplicationError({f'{str(ex)}': 'Failed to create camera'})
        return Response(camera_serializer.CameraSimpleOutputSerializer(camera).data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        filter_serializer = self.FilterDeleteSerializer(data=request.data)
        filter_serializer.is_valid(raise_exception=True)
        validated_data = filter_serializer.validated_data

        list_camera_ids = validated_data.get("cameras")
        try:
            service.remove_list_cameras(list_camera_ids, request.user)
            return Response({'message': 'OK'})
        except IntegrityError as ex:
            logger.exception(ex)
            raise ApplicationError({f'{str(ex)}': 'Failed to bulk delete cameras'})

class CameraDetailView(APIView):
    OutputSerializer = camera_serializer.CameraLocationOutputSerializer
    InputSerializer = camera_serializer.CameraInputSerializer

    def get(self, request, pk): # noqa
        camera = selector.get_camera_detail(pk, user=request.user)
        return Response(self.OutputSerializer(camera).data)

    def put(self, request, pk):
        serializer = self.InputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        try:
            camera = service.update_camera(pk, validated_data, user=request.user)
            return Response(camera_serializer.CameraSimpleOutputSerializer(camera).data)
        except IntegrityError as ex:
            logger.exception(ex)
            raise ApplicationError({f'{str(ex)}': 'Failed to update camera'})

    def delete(self, request, pk): # noqa
        try:
            # Fix remove model relationship
            service.remove_camera(pk, request.user)
            return Response({'message': 'OK'})
        except IntegrityError as ex:
            logger.exception(ex)
            raise ApplicationError({f'{str(ex)}': 'Failed to delete camera'})

class MediaFileError(Exception):
    pass

class CameraSnapShotView(APIView):
    class FilterSerializer(serializers.Serializer):
        # snapshot from camera
        camera_id = serializers.IntegerField(min_value=0, required=False) # field id o trong BaseModel
        start_time = serializers.DateTimeField(default=timezone.make_aware(
            datetime.datetime(2023, 1, 1, 0, 0, 0)))
        end_time = serializers.DateTimeField(default=timezone.now)

        # snapshot from a media file
        url = serializers.CharField(max_length=512, required=False,
                                    validators=[URLValidator(schemes=['http', 'https', 'rtsp'])])

        # time in video to snapshot image (seconds)
        capture_time = serializers.IntegerField(default=DEFAULT_CAPTURE_TIME, min_value=0)

    def post(self, request):
        filter_serializer = self.FilterSerializer(data=request.data)
        filter_serializer.is_valid(raise_exception=True)

        # need to implement

# ===== Vannhk 08/01/2024 =====

        validated_data = filter_serializer.validated_data

        camera_id = validated_data.get('camera_id')
        url = validated_data.get('url')
        results = {}
        # Snapshot logic
        try:
            if camera_id and url:
                snapshot_path = capture_camera_snapshot(camera_id, url)
                results['message'] = "Snapshot captured successfully."
                results['snapshot_path'] = snapshot_path
            else:
                raise ApplicationError("No 'camera id' or 'url' provided.")
        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response(results)

# ==========

