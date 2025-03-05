from django.db.models import CharField
from rest_framework import serializers

from apps.khanhvan.models.camera_alert  import CameraAlert
from apps.khanhvan.models.rule_version import RuleVersion



class CameraAlertFilterSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False)

    Camera = serializers.SerializerMethodField()

    Rule = serializers.SerializerMethodField()

    version_number = serializers.IntegerField(required=False)

    type = serializers.CharField(required=False)
    desc = serializers.CharField(required=False)


    class Meta:
        model = CameraAlert
        fields = ('id', 'Camera', 'Rule', 'version_number', 'type', 'desc')

    def get_Camera(self, obj):
        return {
            "camera_id": obj.camera_id,
            "camera_name": obj.camera_name
        }

    def get_Rule(self, obj):
        return {
            "rule_id": obj.rule_id,
        }

class VersionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleVersion
        fields = '__all__'


class CameraAlertDetailFilterSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False)

    Camera = serializers.SerializerMethodField()

    Rule = serializers.SerializerMethodField()

    version_number = serializers.IntegerField(required=False)
    version_detail = VersionDetailSerializer(required=False)


    type = serializers.CharField(required=False)
    desc = serializers.CharField(required=False)

    class Meta:
        model = CameraAlert
        fields = ('id', 'Camera', 'rule_id', 'version_number', 'version_detail', 'type', 'desc')

    def get_Camera(self, obj):
        return {
            "camera_id": obj.camera_id,
            "camera_name": obj.camera_name
        }
    def get_Rule(self, obj):
        return {
            "rule_id": obj.rule_id,
        }



class CameraAlertDetailWithDeletedVersionFilterSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)

    Camera = serializers.SerializerMethodField()

    Rule = serializers.SerializerMethodField()

    version_detail = serializers.CharField(required = False)

    type = serializers.CharField(required=False)
    desc = serializers.CharField(required=False)

    class Meta:
        model = CameraAlert
        fields = ('id', 'Camera', 'Rule', 'version_detail', 'type', 'desc')

    def get_Camera(self, obj):
        return {
            "camera_id": obj.camera_id,
            "camera_name": obj.camera_name
        }

    def get_Rule(self, obj):
        return {
            "rule_id": obj.rule_id,
        }