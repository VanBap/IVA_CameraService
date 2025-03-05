from django.db import models
from common.base_model import BaseModel
from common import exceptions as module_exceptions

class CameraGroup(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    desc = models.CharField(max_length=512, blank = True, default = "")
    active = models.SmallIntegerField(default = 1)

    objects = models.Manager()

    def custom_clean(self, set_updated_fields = None):
        if (not set_updated_fields) or ('name' in set_updated_fields):
            self.check_unique_name()

    def check_unique_name(self):
        # check name is unique
        group = CameraGroup.objects.only('name').filter(name=self.name).first()
        if not group:
            return

        if not self.id or self.id != group.id:
            raise module_exceptions.GroupNameAlreadyExist()

    class Meta:
        db_table = 'camera_group'
        managed = True