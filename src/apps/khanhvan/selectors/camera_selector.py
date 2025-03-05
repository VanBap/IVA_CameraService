import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django_mysql.models.functions import JSONLength

from api import settings
from utils import misc
from utils.minio_utils import MinioUtil
from ..models.camera import Camera
from ..serializers import camera_serializer
from ..utils import exceptions as module_exceptions

logger = logging.getLogger('app')


def get_user_filter(_user):
    return Q()


def get_camera(camera_id, user, is_updated=False, include_deleted=False):
    try:
        user_filter = get_user_filter(user)
        qs = Camera.global_objects if include_deleted else Camera.objects
        if is_updated:
            qs = qs.select_for_update()

        return qs.filter(user_filter).get(pk=camera_id)
    except ObjectDoesNotExist:
        raise module_exceptions.CameraNotFound()


def get_camera_detail(camera_id, user):
    try:
        user_filter = get_user_filter(user)
        if user_filter:
            return Camera.objects.select_related('group').filter(user_filter).get(pk=camera_id)
        else:
            return Camera.objects.select_related('group').get(pk=camera_id)
    except ObjectDoesNotExist:
        raise module_exceptions.CameraNotFound()


CameraOutputSerializerMaps = {
    'simple': camera_serializer.CameraOnlyNameOutputSerializer,
    'location': camera_serializer.CameraLocationOutputSerializer,

    'normal': camera_serializer.CameraWithGroupOutputSerializer,

    'detector': camera_serializer.CameraDetectorOutputSerializer,

}



def get_group_filters(validated_data):
    my_filter = Q()

    # group
    group_id = validated_data.get('group')
    if group_id:
        my_filter &= Q(group=group_id)

    # groups
    groups = validated_data.get("groups")
    if groups:
        my_filter &= Q(group__in=groups)

    # list camera without Group
    has_group = validated_data.get('has_group')
    if has_group is not None and has_group:
        my_filter &= Q(group__isnull=False)
    elif has_group is not None and not has_group:
        my_filter &= Q(group__isnull=True)

    return my_filter


def get_list_cameras(validated_data, user):
    # filter
    my_filter = get_user_filter(user)

    # group
    my_filter &= get_group_filters(validated_data)

    # camera connection
    conn_status = validated_data.get("conn_status")
    if conn_status:
        my_filter &= Q(conn_status=conn_status)

    # name
    name = validated_data.get('name')
    if name:
        my_filter &= Q(name__icontains=name)

    # cameras
    list_camera_ids = validated_data.get('cameras')
    if list_camera_ids:
        my_filter &= Q(id__in=list_camera_ids)

    # orders
    sort_params = validated_data.get('sort')
    orders = misc.parse_sort_params(sort_params) if sort_params else ['-created_at']

    # return_mode
    return_mode = validated_data.get('return_mode', 'normal')
    if return_mode == 'simple':
        qs = Camera.objects.only('name')
    elif return_mode == 'location' or return_mode == 'live' or return_mode == 'detector':
        qs = Camera.objects
    elif return_mode == 'normal' or return_mode == 'rule':
        qs = Camera.objects.select_related('group')
    else:
        qs = Camera.objects.select_related('group')

    output_serializer_class = CameraOutputSerializerMaps.get(return_mode,
                                                             camera_serializer.CameraSimpleOutputSerializer)

    qs = qs.filter(my_filter).order_by(*orders)

    return qs, output_serializer_class




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


def get_dict_all_cameras(user):
    # user filter
    user_filter = get_user_filter(user)
    list_cameras = Camera.objects.filter(user_filter)

    dict_camera_infos = {}
    for camera in list_cameras:
        dict_camera_infos[camera.id] = camera

    return dict_camera_infos


def get_dict_cameras(list_camera_ids, user):
    if not list_camera_ids:
        return {}

    # user filter
    user_filter = get_user_filter(user)
    list_cameras = Camera.objects.filter(user_filter).filter(id__in=list_camera_ids)

    # parse response
    dict_camera_infos = {}
    for camera in list_cameras:
        dict_camera_infos[camera.id] = camera

    return dict_camera_infos


def validate_list_camera_ids(list_camera_ids, user):
    if not list_camera_ids:
        return {}

    dict_cameras = get_dict_cameras(list_camera_ids, user)
    for camera_id in list_camera_ids:
        if camera_id not in dict_cameras:
            raise module_exceptions.CameraNotFound(f'Camera {camera_id} not found')

    return dict_cameras
