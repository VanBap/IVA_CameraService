import logging
import time
from django.db import transaction

from api import settings
from common import drf
from utils.minio_utils import MinioUtil
# === Vannhk ===
from ..models.camera import Camera
from ..selectors import camera_selector, camera_group_selector
from ..utils import exceptions as module_exceptions
from utils import video_utils

logger = logging.getLogger('app')


def process_background_url(validated_data):
    # check background url
    background_url = validated_data.get('background_url')
    if background_url:
        try:
            validated_data['background_url'] = MinioUtil.upload_file(background_url,
                                                                     root_folder=settings.ROOT_FOLDER_CAMERA,
                                                                     check_image=True)
        except Exception as ex:
            logger.exception(ex)
            raise module_exceptions.CameraBackgroundInvalid({'background_url': 'Background url is invalid!'})


@transaction.atomic 
def create_camera(validated_data, user):
    # add user_id to validated_data
    validated_data['user_id'] = getattr(user, 'id', None)

    url = validated_data.get('url')
    background_url = '/home/vbd-vanhk-l1-ubuntu/work/image_{}.jpg'.format(time.time())
    video_utils.extract_thumbnail(url, background_url)
    validated_data['background_url'] = background_url

    # check group
    # field name "group" is ForeignField, need to pop from validated_data
    # only use field "group_id"
    group_id = validated_data.pop('group', None)
    if group_id:
        group = camera_group_selector.get_camera_group(group_id)
        validated_data['group_id'] = group.id

    # create camera with group
    return drf.model_create(Camera, validated_data)


@transaction.atomic
def update_camera(camera_id, validated_data, user):
    # add user_id to validated_data
    validated_data['user_id'] = getattr(user, 'id', None)

    # check group id
    if 'group' in validated_data:
        # field name "group" is ForeignField, need to pop from validated_data
        # only use field "group_id"
        group_id = validated_data.pop('group')
        if group_id is None:
            # clear group_id
            validated_data['group_id'] = None
        else:
            group = camera_group_selector.get_camera_group(group_id)
            validated_data['group_id'] = group.id

    # check background url
    process_background_url(validated_data)

    # UPDATE CAMERA
    camera = camera_selector.get_camera(camera_id, user, is_updated=True)
    drf.model_update(camera, validated_data)
    return camera


@transaction.atomic
def remove_camera(camera_id, user):
    camera = camera_selector.get_camera(camera_id, user, is_updated=True)

    # delete all reversed field
    # example: camera.rule_configs.all().delete()

    # soft delete Camera
    camera.delete()


def remove_list_cameras(list_camera_ids, user):
    for cam_id in list_camera_ids:
        remove_camera(cam_id, user)
