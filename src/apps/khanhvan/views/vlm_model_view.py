import logging

from django.db import IntegrityError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common import drf
from common.drf import PageNumberPagination
from common.exceptions import ApplicationError

from ..serializers import vlm_model_serializer
from ..services import vlm_model_service as service
# from ..urls import vlm_model_urls

logger = logging.getLogger('app')


class VLMListView(APIView):

    OutputSerializer = vlm_model_serializer.VLMmodelSerializer
    InputSerializer = vlm_model_serializer.VLMmodelSerializer

    class FilterSerializer(serializers.Serializer):
        aimodel_name = serializers.CharField(required=False) # <= required = False
        aimodel_key = serializers.CharField(required=False)

    def get(self, request):

        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        validated_data = filter_serializer.validated_data

        list_ai_models = service.get_list_ai_models(validated_data)

        if validated_data.get('all'):
            return Response({
                "results": self.OutputSerializer(list_ai_models, many=True).data
            })

        return drf.get_paginated_response( # phan trang
            pagination_class = drf.PageNumberPagination,
            serializer_class = self.OutputSerializer,
            queryset = list_ai_models,
            request = request,
            view = self
        )

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            aimodel = service.create_ai_model(validated_data, user=request.user)
            return Response(self.OutputSerializer(aimodel).data, status=status.HTTP_201_CREATED)

        except IntegrityError as ex:
            logger.error('Failed to create new ai model')
            raise ApplicationError({f'{str(ex)}': 'Database error'})


class VLMDetailView(APIView):
    OutputSerializer = vlm_model_serializer.VLMmodelSerializer
    InputSerializer = vlm_model_serializer.VLMmodelSerializer

    def get(self, request, pk):
        vlmmodel = service.get_vlm_model(pk)

        res = self.OutputSerializer(vlmmodel).data

        return Response(res)

    def delete(self, request, pk):
        try:
            check = service.remove_vlm_model(pk)
            if check != True:
                return Response({'message': f'Please remove rule id: {check} in advanced'})

            return Response({'message': 'Successfully deleted ai model'})
        except IntegrityError as ex:
            logger.exception(ex)
            raise ApplicationError({f'{str(ex)}': 'Failed to delete ai model'})