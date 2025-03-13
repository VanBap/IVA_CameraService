from django.db import models
from django_filters import CharFilter

from common.base_model import BaseModel

class VLMModel(BaseModel):

    name = models.CharField(max_length=255, default='', blank=True)
    code_name = models.CharField(max_length=255, default='')
    api_key = models.TextField(default='', blank=True)
    url = models.CharField(max_length=255, default='', blank=True)

    class Meta:
        managed = True
        db_table = 'vlm_model'