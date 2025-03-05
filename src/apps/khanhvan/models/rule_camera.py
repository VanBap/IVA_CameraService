from django.db import models

from common.base_model import BaseModel
from ..models.camera import Camera
from ..models.rule import Rule

class RuleCamera(BaseModel):
    rule = models.ForeignKey(Rule, on_delete=models.DO_NOTHING, related_name='camera_configs') # Rule.camera_configs -> RuleCamera
    camera = models.ForeignKey(Camera, on_delete=models.DO_NOTHING, related_name='rule_configs')

    # unique rule.id + camera.id


    class Meta:
        managed = True
        db_table = 'rule_camera'

        # UNIQUE rule + version_number
        constraints = [
            models.UniqueConstraint(
                fields=['rule', 'camera'],
                name='unique_rule_camera'
            )
        ]
