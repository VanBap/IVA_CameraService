import logging

from rest_framework import serializers

# === Vannhk ===
from ..models.prompt import Prompt



logger = logging.getLogger('app')

class PromptSerializer(serializers.ModelSerializer):

    class Meta:
        model = Prompt
        fields = '__all__'

