import logging

from django.db import IntegrityError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common import drf
from common.drf import PageNumberPagination
from common.exceptions import ApplicationError

from ..services import chatbot_service

logger = logging.getLogger('app')

class ChatbotView(APIView):

    # def get(self, request):
    #
    #     return Response({
    #         "results": self.OutputSerializer(list_ai_models, many=True).data
    #     })


    def post(self, request):

        try:
            response = chatbot_service.chatbot_run(request.data)
            return Response(response, status=status.HTTP_201_CREATED)

        except IntegrityError as ex:
            logger.error('Failed to run Chatbot')
            raise ApplicationError({f'{str(ex)}': 'Chatbot error'})