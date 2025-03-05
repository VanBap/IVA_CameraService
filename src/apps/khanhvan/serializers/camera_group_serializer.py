from rest_framework import serializers
# === Vannhk ===
from ..models.camera_group import CameraGroup
from ..models.camera import Camera
from common import drf
from utils.minio_utils import MinioUtil


class CameraGroupOnlyNameOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraGroup
        fields = ['id', 'name']


class CameraGroupOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraGroup
        fields = ['id', 'name', 'desc', 'active', 'created_at']


class CameraSimpleOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = ['id', 'name']


class CameraSimpleWithUrlOutputSerializer(serializers.ModelSerializer):
    background_link = serializers.SerializerMethodField()
    synopsis_video_link = serializers.SerializerMethodField()

    def get_background_link(self, camera):  # noqa
        return MinioUtil.get_absolute_url(camera.background_url)

    class Meta:
        model = Camera
        fields = ['id', 'name', 'url', 'background_url', 'background_link',
                  'created_at', 'updated_at', 'conn_status',
                  'desc']


class CameraGroupWithCameraOutputSerializer(serializers.ModelSerializer):
    cameras = serializers.SerializerMethodField()

    class Meta:
        model = CameraGroup
        fields = ['id', 'name', 'cameras']

    def get_cameras(self, obj):
        queryset = obj.cameras.all()
        camera_ids = self.context.get('camera_ids')
        if camera_ids:
            queryset = queryset.filter(id__in=camera_ids)
        return CameraSimpleWithUrlOutputSerializer(queryset, many=True).data


class CameraGroupInputSerializer(drf.SafeInputModelSerializer):
    # disable unique check of drf
    cameras = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )

    class Meta:
        model = CameraGroup
        fields = '__all__'
