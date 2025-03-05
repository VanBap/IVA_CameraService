from django.db import models

from .rule import Rule
from common.base_model import BaseModel

class RulePrompt(BaseModel):

    prompt = models.CharField(max_length=500)

    class Meta:
        managed = True
        db_table = "rule_prompt"
