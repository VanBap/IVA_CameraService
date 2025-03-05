from django.db import models
from django_filters import CharFilter

from common.base_model import BaseModel

class AImodel(BaseModel):

    aimodel_name = models.CharField(max_length=255)
    aimodel_apikey = models.CharField(max_length=255, unique=True)

    class Meta:
        managed = True
        db_table = 'ai_model'