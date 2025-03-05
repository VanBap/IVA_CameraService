import logging

from rest_framework import serializers

# === Vannhk ===
from ..models.ai_model import AImodel



logger = logging.getLogger('app')

class AImodelSerializer(serializers.ModelSerializer):

    class Meta:
        model = AImodel
        fields = '__all__'

