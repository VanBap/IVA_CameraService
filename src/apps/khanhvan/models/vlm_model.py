from django.db import models
from django_filters import CharFilter

from common.base_model import BaseModel

class VLMModel(BaseModel):

    vlmmodel_name = models.CharField(max_length=255)
    vlmmodel_apikey = models.TextField()
    vlmmodel_url = models.CharField(max_length=255, default='', blank=True)

    class Meta:
        managed = True
        db_table = 'vlm_model'