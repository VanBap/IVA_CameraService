import logging

from rest_framework import serializers

# === Vannhk ===
from ..models.camera import Camera
from ..models.rule import Rule
from ..models.rule_camera import RuleCamera

from ..models.vlm_model import VLMModel
from ..models.prompt import Prompt



logger = logging.getLogger('app')

class CameraSerializer(serializers.ModelSerializer):

    class Meta:
        model = Camera
        fields = ['id', 'name']

class RuleCameraDetailOutputSerializer(serializers.ModelSerializer):
    camera_id = serializers.IntegerField(source='camera.id') # RuleCamera.camera.id

    class Meta:
        model = RuleCamera
        exclude = ['rule']

class RuleVlmOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = VLMModel
        fields = ['id', 'code_name']

class RulePromptOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prompt
        fields = ['id', 'content']

class RuleWithCameraOutputSerializer(serializers.ModelSerializer):

    camera_configs = CameraSerializer(source='cameras', many=True) # rule.cameras
    vlm_model = RuleVlmOutputSerializer(required=False)
    prompt = RulePromptOutputSerializer(required=False)

    class Meta:
        model = Rule
        fields = ['name', 'type', 'id', 'start_time', 'end_time', 'current_version', 'camera_configs', 'prompt', 'vlm_model']


class RuleInputSerializer(serializers.ModelSerializer):

    # list
    # Hien tai: camera_configs <=> list_camera_ids
    camera_configs = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )

    prompt_id = serializers.IntegerField(required=False)
    vlm_model_id = serializers.IntegerField(required=False)

    class Meta:
        model = Rule
        fields = '__all__'

class RuleDetailOutputSerializer(serializers.ModelSerializer):
    # 02/02/25
    camera_configs = RuleCameraDetailOutputSerializer(many=True, required=False) # Rule.camera_configs -> RuleCamera
    vlm_model = RuleVlmOutputSerializer(required=False)
    prompt = RulePromptOutputSerializer(required=False)

    class Meta:
        model = Rule
        fields = ['name', 'type', 'id', 'created_at', 'updated_at', 'created_by', 'updated_by',  'start_time', 'end_time', 'current_version', 'camera_configs', 'prompt', 'vlm_model']


class CameraDetailOutputSerializer(serializers.ModelSerializer):
    camera_id = serializers.IntegerField(source='id') # Camera.id

    class Meta:
        model = Camera
        fields = '__all__'


class RuleDetailOutputSerializerV2(serializers.ModelSerializer):
    # 02/02/25
    cameras = CameraDetailOutputSerializer(many=True, required=False) # Rule.cameras

    class Meta:
        model = Rule
        fields = '__all__'
        # exclude = ['cameras']

