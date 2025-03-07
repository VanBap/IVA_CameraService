import logging

from rest_framework import serializers

# === Vannhk ===
from ..models.vlm_model import VLMModel



logger = logging.getLogger('app')

class VLMmodelSerializer(serializers.ModelSerializer):

    class Meta:
        model = VLMModel
        fields = '__all__'

