import logging

from django.db import IntegrityError
from django.http import JsonResponse
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common import drf
from common.drf import PageNumberPagination
from common.exceptions import ApplicationError

from ..services import chatbot_IVA_DEMO, chatbot_SAPO_DEMO
from ..services.chatbot_IVA_DEMO import is_valid_query
logger = logging.getLogger('app')

class ChatbotView(APIView):

    # def get(self, request):
    #
    #     return Response({
    #         "results": self.OutputSerializer(list_ai_models, many=True).data
    #     })


    def post(self, request):

        try:
            text = request.data["question"].lower()
            print(type(text))
            print(f"text: {text}")
            if not is_valid_query(text):

                return JsonResponse({"answer": "Vui lòng nhập một câu hỏi rõ ràng, bạn cần hướng dẫn gì về IVA (bằng tiếng Việt)?"})

                # response={{"Error": "Vui lòng nhập một câu hỏi rõ ràng bạn cần hướng dẫn về IVA (bằng tiếng Việt)"}}
                # return Response(response, status=status.HTTP_201_CREATED)

            response = chatbot_IVA_DEMO.chatbot_run(request.data)
            return Response(response, status=status.HTTP_201_CREATED)

        except IntegrityError as ex:
            logger.error('Failed to run Chatbot')
            raise ApplicationError({f'{str(ex)}': 'Chatbot error'})