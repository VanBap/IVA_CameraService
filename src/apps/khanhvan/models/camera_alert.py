from django.db import models

from common.base_model import BaseSimpleModel
from .camera import Camera
from .rule import Rule

class CameraAlert(BaseSimpleModel):

    camera_id = models.IntegerField(null=True, default=0)
    rule_id = models.IntegerField(null=True, default=0)
    version_number = models.IntegerField(null=True, default=None)

    type = models.CharField(max_length=255, default='')
    desc = models.CharField(max_length=255, default='')

    class Meta:
        db_table = 'camera_alert'
        managed = False