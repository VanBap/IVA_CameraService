import logging

from django.db import IntegrityError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common import drf
from common.drf import PageNumberPagination
from common.exceptions import ApplicationError

from ..serializers import prompt_serializer
from ..services import prompt_service as service

logger = logging.getLogger('app')


class PromptListView(APIView):

    OutputSerializer = prompt_serializer.PromptSerializer
    InputSerializer = prompt_serializer.PromptSerializer

    class FilterSerializer(serializers.Serializer):
        prompt_id = serializers.IntegerField(required=False) # <= required = False

    def get(self, request):

        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        validated_data = filter_serializer.validated_data

        list_prompts = service.get_list_prompts(validated_data)

        if validated_data.get('all'):
            return Response({
                "results": self.OutputSerializer(list_prompts, many=True).data
            })

        return drf.get_paginated_response( # phan trang
            pagination_class = drf.PageNumberPagination,
            serializer_class = self.OutputSerializer,
            queryset = list_prompts,
            request = request,
            view = self
        )

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            prompt = service.create_prompt(validated_data, user=request.user)
            return Response(self.OutputSerializer(prompt).data, status=status.HTTP_201_CREATED)

        except IntegrityError as ex:
            logger.error('Failed to create new ai model')
            raise ApplicationError({f'{str(ex)}': 'Database error'})


class PromptDetailView(APIView):
    OutputSerializer = prompt_serializer.PromptSerializer
    InputSerializer = prompt_serializer.PromptSerializer

    def get(self, request, pk):
        prompt = service.get_prompt(pk)

        res = self.OutputSerializer(prompt).data

        return Response(res)

    def delete(self, request, pk):
        try:
            service.remove_prompt(pk)
            return Response({'message': 'Successfully deleted prompt'})
        except IntegrityError as ex:
            logger.exception(ex)
            raise ApplicationError({f'{str(ex)}': 'Failed to delete prompt'})