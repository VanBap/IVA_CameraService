from django.db import models
from django_filters import CharFilter

from common.base_model import BaseModel

class Prompt(BaseModel):

    content = models.TextField()

    class Meta:
        managed = True
        db_table = 'prompt'