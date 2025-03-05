import logging

from rest_framework import serializers

from ..models import RuleCamera
# === Vannhk ===
from ..models.camera import Camera
from ..models.rule import Rule
from ..models.rule_version import RuleVersion

class RuleVersionInputSerializer(serializers.ModelSerializer):

    class Meta:
        model = RuleVersion
        fields = '__all__'

class RuleCameraConfigs(serializers.ModelSerializer):

    class Meta:
        model = Rule
        fields = ['cameras']

class RuleVersionOutputSerializer(serializers.ModelSerializer):
    cameras_in_rule = RuleCameraConfigs(source='rule', required=False) # RuleVersion.rule

    class Meta:
        model = RuleVersion
        fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by', 'version_number', 'name', 'type', 'start_time', 'end_time', 'rule', 'cameras_in_rule']




class RuleVersionGeneralOutputSerializer(serializers.ModelSerializer):
    version_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = RuleVersion
        fields = ['rule_id', 'version_id', 'version_number', 'name']