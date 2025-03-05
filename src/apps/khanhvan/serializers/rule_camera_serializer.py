import logging
from rest_framework import serializers
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from common import drf

from ..utils.helpers import get_url_for_detector
from ..utils import exceptions as module_exceptions
from utils.minio_utils import MinioUtil

# === Vannhk ===
from ..models.camera import Camera
from ..models.rule import Rule
from ..models.rule_camera import RuleCamera

class RuleCameraInputSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    camera_id = serializers.IntegerField()