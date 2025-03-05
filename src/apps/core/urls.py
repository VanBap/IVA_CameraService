from django.urls import path
from .views.health_check import HealthCheckView
from .views import core_view


urlpatterns = [
    path('health-check', HealthCheckView.as_view()),
    path('upload', core_view.UploadFileView.as_view()),
    path('utils/get-base64-data', core_view.Base64View.as_view()),
]
