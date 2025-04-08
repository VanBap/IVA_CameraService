from django.urls import path, include
from .views import (
    chatbot_view
)

app_name = ('chatbot')

#chatbot
chatbot_urls=[
    path('',chatbot_view.ChatbotView.as_view())
]

urlpatterns = [
    path('vannhkchatbot/', include(chatbot_urls)),
]