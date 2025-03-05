from typing import Optional
from enum import IntEnum

from strenum import StrEnum
from django.db import models

from common.base_model import BaseModel
from common.my_soft_delete_model import MySoftDeleteModel
from utils.minio_utils import MinioUtil
from api import settings

from .camera_group import CameraGroup
from ..utils import exceptions as module_exception

STREAM_FRAME_WIDTH = 1280
STREAM_FRAME_HEIGHT = 720
DEFAULT_FIRST_SAMPLE_TIME = 0
DEFAULT_INTERVAL_SAMPLE_TIME = 20

class ConnStatus(IntEnum):
    CONNECT: int = 1
    NOT_CONNECT: int = 2
    PASSWORD_INVALID: int = 3

class Camera(BaseModel, MySoftDeleteModel):
    name = models.CharField(max_length=255)

    desc = models.CharField(max_length=1024, blank = True, default = '')

    url = models.CharField(max_length=255, default='',blank=True)

    background_url = models.CharField(max_length=255, default='', blank=True)
    background_width = models.IntegerField(null=True, default=0)
    background_height = models.IntegerField(null=True, default=0)


    # Camera group
    group = models.ForeignKey(CameraGroup, on_delete=models.DO_NOTHING, null=True, related_name='cameras')
    conn_status = models.IntegerField(null=True, default=ConnStatus.NOT_CONNECT)

    class Meta:
        db_table = 'camera'
        managed = True

        constraints = [
            models.UniqueConstraint(fields=['name', 'deleted_at'], name = 'unique_active_camera_name'), # ko co 2 hang nao trong cung 1 field co cung gia tri
        ]

    def custom_clean(self, set_updated_fields = None): #noqa

        # check name is unique
        # if insert new camera or update camera name
        if (not set_updated_fields) or ('name' in set_updated_fields or 'deleted_at' in set_updated_fields):
            self.check_unique_name()

    def check_unique_name(self):
        camera = Camera.global_objects.only('name').filter(name = self.name, deleted_at = self.deleted_at).first()
        if not camera:
            return

        if not self.id or self.id != camera.id:
            raise module_exception.CameraNameAlreadyExist()

    def get_background_link(self):
        return MinioUtil.get_absolute_url(self.background_url)

        





































