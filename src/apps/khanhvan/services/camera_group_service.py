import logging
from django.db import transaction

from common import drf
from common.enums import ActorType
from ..selectors import camera_selector, camera_group_selector
from ..models.camera import CameraGroup
from django.utils import timezone
logger = logging.getLogger('app')


@transaction.atomic
def create_camera_group(validated_data: dict, user):
    user_id = getattr(user, 'id', None)
    validated_data['user_id'] = user_id

# === Clear code implement ===

    # check exist cameras
    cameras = validated_data.pop('cameras', [])

    user_id = validated_data.pop('user_id', None) or ActorType.SYSTEM
    dict_cameras = camera_selector.validate_list_camera_ids(cameras, user)

    # # create group
    # group = CameraGroup(**validated_data)
    # group.created_by = user_id
    # group.create_at = timezone.now()
    # group.updated_by = user_id
    # group.updated_at = timezone.now()
    # group.save()
    # return group

# === Use Create function in drf ===
    camera_group = drf.model_create(CameraGroup, validated_data)
    # add camera to group
    if dict_cameras:
        for cam in dict_cameras.values():
            drf.model_update(cam, {'group_id': camera_group.id, 'user_id': user_id})
    return camera_group


@transaction.atomic
def update_camera_group(group_id: int, validated_data: dict, user):
    user_id = getattr(user, 'id', None)
    validated_data['user_id'] = user_id

    # check exist cameras
    cameras = validated_data.pop('cameras', [])
    dict_cameras = camera_selector.validate_list_camera_ids(cameras, user)

    # update group
    group = camera_group_selector.get_camera_group(group_id=group_id, is_updated=True)
    drf.model_update(group, validated_data)

    # replace list cameras
    if dict_cameras is not None:
        # (fastest method: group.set(dict_cameras.values()), but cannot set field updated_by)

        # clear current list cameras
        group.cameras.clear()

        # set new list cameras of group
        for cam in dict_cameras.values():
            # need force update field group_id
            # because a camera can be removed from group when call group.cameras.clear() above
            drf.model_update(cam, {'group_id': group.id, 'user_id': user_id}, force_updated_fields=['group_id'])

    return group


@transaction.atomic
def remove_camera_group(group_id):
    group = camera_group_selector.get_camera_group(group_id=group_id, is_updated=True)
    # set camera.group_id = None for all cameras including deleted cameras
    group.cameras(manager='global_objects').clear()
    group.delete()


def remove_list_camera_groups(list_group_ids):
    res = {}
    for group_id in list_group_ids:
        try:
            remove_camera_group(group_id=group_id)
            res[group_id] = {
                'message': 'OK'
            }
        except Exception as ex:
            logger.exception(ex)
            res[group_id] = {
                'code': 'failed',
                'message': str(ex)
            }
    return res


@transaction.atomic
def add_camera_into_group(group_id, validated_data, user):
    user_id = getattr(user, 'id', None)

    # validate cameras
    cameras = validated_data.get("cameras")
    dict_cameras = camera_selector.validate_list_camera_ids(cameras, user)

    # get group
    group = camera_group_selector.get_camera_group(group_id=group_id, is_updated=True)

    # add cameras
    if dict_cameras:
        for cam in dict_cameras.values():

            # === Clear code ===
            cam.group_id = group_id
            cam.save()

            # === Use function ===
            # drf.model_update(cam, {'group_id': group.id, 'user_id': user_id})

    # Update group (updated_at, updated_by)
    # === Clear code ===
    group.updated_by = user_id
    group.updated_at = timezone.now()
    group.save()

    # === Use function ===
    # return drf.model_update(group, {'user_id': user_id})
    return group


@transaction.atomic
def remove_camera_from_group(group_id, validated_data, user):
    user_id = getattr(user, 'id', None)

    # check list of cameras
    cameras = validated_data.get("cameras")
    dict_cameras = camera_selector.validate_list_camera_ids(cameras, user)

    # get group
    group = camera_group_selector.get_camera_group(group_id=group_id, is_updated=True)

    if dict_cameras:
        # remove camera from group
        for cam in dict_cameras.values():
            # check if cam is in this group
            if cam.group_id == group.id:
                drf.model_update(cam, {'group_id': None, 'user_id': user_id})

    # Update group (updated_at, updated_by)
    return drf.model_update(group, {'user_id': user_id})
