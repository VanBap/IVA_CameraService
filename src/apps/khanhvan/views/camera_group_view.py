import logging

from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.utils import IntegrityError

from common import drf
from common.exceptions import ApplicationError
from ..services import camera_group_service as service
from ..selectors import camera_group_selector as selector, camera_selector
from ..serializers import camera_group_serializer as group_serializer

logger = logging.getLogger('app')


class CameraGroupView(APIView):
    InputSerializer = group_serializer.CameraGroupInputSerializer
    OutputSerializer = group_serializer.CameraGroupOutputSerializer

    class FilterSerializer(serializers.Serializer):
        name = serializers.CharField(required=False)
        sort = serializers.CharField(required=False)

    class FilterDeleteSerializer(serializers.Serializer):
        groups = serializers.ListField(
            child=serializers.IntegerField(), required=True
        )

    def get(self, request):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        validated_data = filter_serializer.validated_data

        # get list of camera groups
        groups = selector.get_list_camera_groups(validated_data)

        return drf.get_paginated_response(
            pagination_class=drf.PageNumberPagination,
            serializer_class=self.OutputSerializer,
            queryset=groups,
            request=request,
            view=self
        )

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        group = service.create_camera_group(validated_data=validated_data,
                                            user=request.user)
        return Response(self.OutputSerializer(group).data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        serializer = self.FilterDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        list_group_ids = validated_data.get("groups")
        try:
            res = service.remove_list_camera_groups(list_group_ids=list_group_ids)
            return Response(res)
        except IntegrityError as ex:
            logger.exception(ex)
            raise ApplicationError({f'{str(ex)}': 'Failed to bulk delete camera groups'})


class CameraGroupDetailView(APIView):
    InputSerializer = group_serializer.CameraGroupInputSerializer
    OutputSerializer = group_serializer.CameraGroupOutputSerializer

    def get(self, request, pk): # noqa
        group = selector.get_camera_group(pk)
        return Response(self.OutputSerializer(group).data)

    def put(self, request, pk):
        serializer = self.InputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        try:
            camera_group = service.update_camera_group(pk, validated_data, request.user)
            return Response(self.OutputSerializer(camera_group).data)
        except IntegrityError as ex:
            logger.exception(ex)
            raise ApplicationError({f'{str(ex)}': 'Database error'})

    def delete(self, request, pk): # noqa
        try:
            service.remove_camera_group(pk)
            return Response({'message': 'OK'})
        except IntegrityError as ex:
            logger.exception(ex)
            raise ApplicationError({f'{str(ex)}': 'Database error'})


class CameraGroupListCameraView(APIView):
    class FilterSerializer(serializers.Serializer):
        name = serializers.CharField(required=False)
        sort = serializers.CharField(required=False)
        all = serializers.BooleanField(required=False)
        return_mode = serializers.CharField(default='all')

    class InputSerializer(serializers.Serializer):
        cameras = serializers.ListField(
            child=serializers.IntegerField(min_value=0)
        )

    def get(self, request, pk):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        validated_data = filter_serializer.validated_data

        # check group
        group_id = pk
        selector.get_camera_group(group_id)

        # get list camera of group
        validated_data['group'] = group_id
        cameras, output_serializer_class = camera_selector.get_list_cameras(validated_data, user=request.user)
        if validated_data.get('all'):
            return Response({
                "results": output_serializer_class(cameras, many=True).data
            })

        return drf.get_paginated_response(
            pagination_class=drf.PageNumberPagination,
            serializer_class=output_serializer_class,
            queryset=cameras,
            request=request,
            view=self
        )

    def post(self, request, pk):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        service.add_camera_into_group(pk, validated_data, request.user)
        return Response({'message': 'OK'})

    def delete(self, request, pk):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        service.remove_camera_from_group(pk, validated_data, request.user)
        return Response({'message': 'OK'})
