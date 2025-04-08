from typing import Optional
from enum import IntEnum

from strenum import StrEnum
from django.db import models

from common.base_model import BaseModel
from common.my_soft_delete_model import MySoftDeleteModel
from utils.minio_utils import MinioUtil
from api import settings

class TestImage(BaseModel):
    url = models.CharField(max_length=255, default='', blank=True)

    class Meta:
        db_table = 'test_image'
        managed = True
