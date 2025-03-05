import logging

from django.core.exceptions import ObjectDoesNotExist

from utils import misc
from ..models.camera import CameraGroup
from ..utils import exceptions as module_exceptions

logger = logging.getLogger('app')


def get_camera_group(group_id, is_updated=False):
    try:
        qs = CameraGroup.objects.select_for_update() if is_updated else CameraGroup.objects
        return qs.get(pk=group_id)
    except ObjectDoesNotExist:
        raise module_exceptions.CameraGroupNotFound()


def get_list_camera_groups(validated_data):
    qs = CameraGroup.objects.all()

    # filter
    name = validated_data.get('name')
    if name:
        qs = qs.filter(name__icontains=name)

    # orders
    sort_params = validated_data.get('sort')
    orders = misc.parse_sort_params(sort_params) if sort_params else ['-created_at']

    return qs.order_by(*orders)
