import logging
from rest_framework import serializers
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from common import drf

from ..utils.helpers import get_url_for_detector

# === Vannhk ===
from ..models.camera import Camera


from ..utils import exceptions as module_exceptions
from utils.minio_utils import MinioUtil

logger = logging.getLogger('app')


class CameraOnlyNameOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera        # Mo hinh du lieu lien ket
        fields = ['id', 'name']     # Cac truong se duoc bao gom


class CameraSimpleOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ['id', 'name', 'url', 'background_url',
                  'created_at', 'updated_at', 'conn_status', 'desc']


class CameraWithGroupOutputSerializer(CameraSimpleOutputSerializer):
    group = serializers.SerializerMethodField()

    def get_group(self, camera: Camera):  # noqa
        if camera.group is None:
            return None
        return {
            'id': camera.group.id,
            'name': camera.group.name
        }

    class Meta:
        model = Camera
        fields = ['id', 'name', 'group',
                  'created_at', 'updated_at', 'conn_status', 'desc']


class CameraDetectorOutputSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Camera
        fields = ['id', 'name', 'url']

    def get_url(self, camera: Camera): # noqa
        return get_url_for_detector(camera)


class CameraLocationOutputSerializer(CameraSimpleOutputSerializer):
    class Meta:
        model = Camera
        fields = ['id', 'name', 'desc']

class CameraAllWithPasswordOutputSerializer(CameraWithGroupOutputSerializer):
    vms_name = serializers.SerializerMethodField()

    class Meta:
        model = Camera
        fields = ['id', 'name', 'group', 'url',
                  'background_width', 'background_height',
                  'created_at', 'updated_at', 'conn_status',
                  'desc']

class CameraInputSerializer(drf.SafeInputModelSerializer):
    # re-define group (ForeignField), service will take care of validating this field
    # set null to clear group_id of camera
    group = serializers.IntegerField(required=False, allow_null=True)

    vms_id = serializers.IntegerField(required=False, allow_null=True)

    background_url = serializers.CharField(required=False, max_length=255, allow_blank=True)

    class Meta:
        model = Camera
        fields = '__all__'

    def validate_background_url(self, url): # noqa
        if not url:
            return url

        norm_url = MinioUtil.normalize_url(url)
        try:
            URLValidator()(norm_url)
        except DjangoValidationError:
            raise module_exceptions.CameraBackgroundInvalid()

        return url

    def validate_advanced_config(self, advanced_config): # noqa
        if not isinstance(advanced_config, dict):
            raise module_exceptions.ValidationError('Must be a dict')
        return advanced_config


