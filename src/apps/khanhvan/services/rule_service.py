import logging
import time

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q, Prefetch
from django.utils import timezone

from common.enums import ActorType
from common.my_exception_handler import get_formatted_error_message, DRFFormatterType

from ..utils import exceptions as module_exceptions

from common.exceptions import InvalidInputError

# === Vannhk ===
from ..models.camera import Camera
from ..models import Rule, RuleCamera, RuleVersion
from ..models.camera_alert import CameraAlert


logger = logging.getLogger('app')

def get_list_rules(validated_data):
    # filter rule
    my_filter = Q()

    # name
    name = validated_data.get('name')
    if name:
        my_filter &= Q(name__icontains=name)

    # list of rule ids
    list_rule_ids = validated_data.get('rules')
    if list_rule_ids:
        my_filter &= Q(id__in=list_rule_ids)

    qs = Rule.objects.prefetch_related('cameras').order_by('id')

    return qs.filter(my_filter)

@transaction.atomic
def create_rule(validated_data, user):
    # ================= add them Rule =================
    # add user_id to validated_data
    validated_data['user_id'] = getattr(user, 'id', None)
    user_id = validated_data.pop('user_id', None) or ActorType.SYSTEM

    actor = user_id
    validated_data['created_by'] = actor
    validated_data['updated_by'] = actor

    camera_configs = validated_data.pop('camera_configs', None)
    if not camera_configs:
        raise InvalidInputError({'camera_configs': 'List of camera config is empty'})

    list_camera_ids = []
    # Hien tai: config <=> camera_id
    for config in camera_configs:
        list_camera_ids.append(config)

    # create rule
    # rule = drf.model_create(Rule, validated_data)

    # === add them vao Rule ===
    rule = Rule(**validated_data)
    rule.save()

    # ================= add them RuleCamera =================
    list_rule_cameras = []

    # Check - Kiem tra xem id co loi khong ?
    refer_list_camera_id = list(Camera.objects.all().values_list('id', flat=True))

    for camera_id in camera_configs:
        if camera_id not in refer_list_camera_id:
            raise module_exceptions.CameraNotFound(f'Camera {camera_id} not found')
        else:
    # Neu khong loi:
            rule_camera = RuleCamera()
            rule_camera.camera_id = camera_id
            rule_camera.rule_id = rule.id
            rule_camera.created_by = actor
            rule_camera.updated_by = actor

        list_rule_cameras.append(rule_camera)

    RuleCamera.objects.bulk_create(list_rule_cameras)

    # ================= add them RuleVersion =================
    rule_version = RuleVersion.objects.create(
        rule = rule,
        version_number = rule.current_version,
        name = rule.name,
        type = rule.type,
        start_time = rule.start_time,
        end_time = rule.end_time,
        created_by = rule.created_by,
        updated_by = rule.updated_by,
    )
    rule_version.save()

    return rule

def get_rule(rule_id):
    try:
        qs = Rule.objects
        rule = qs.distinct().get(pk=rule_id)
    except ObjectDoesNotExist:
        raise module_exceptions.RuleNotFound('Rule not found')

    return rule

# lay danh sach cac Camera Alert gan voi rule_id
def get_camera_alert_with_rule (rule_id):

    try:
        qs = CameraAlert.objects.filter(rule_id = rule_id)

    except ObjectDoesNotExist:
        raise module_exceptions.RuleNotFound('Camera Alert not found')

    return qs

# lay danh sach cac RuleVersion gan voi rule_id
def get_rule_version_with_rule (rule_id):
    try:
        qs = RuleVersion.objects.filter(rule_id = rule_id)

    except ObjectDoesNotExist:
        raise module_exceptions.RuleNotFound('Rule Version not found')

    return qs

@transaction.atomic
def remove_rule(rule_id):
    rule = get_rule(rule_id)
    logger.info(" ========== AFTER GET RULE ======")

    # delete rule_camera
    rule.camera_configs.all().delete()
    logger.info(" ========== AFTER DELETE RULE CONFIGS ======")

    # # delete camera alert with rule
    # camera_alert_with_rule = get_camera_alert_with_rule(rule_id)
    # camera_alert_with_rule.delete()
    # logger.info(" ========== AFTER DELETE CAMERA ALERT ======")

    # rule_version_with_rule = get_rule_version_with_rule(rule_id)
    # rule_version_with_rule.delete()
    # logger.info(" ========== AFTER DELETE RULE VERSION ======")

    rule.delete()
    logger.info(" ========== AFTER DELETE RULE ======")

def remove_list_rules(list_rule_ids):
    res = {}

    for rule_id in list_rule_ids:
        try:
            remove_rule(rule_id)
            res[rule_id] = {
                'code': 'success'
            }

        except Exception as ex:
            res[rule_id] = {
                'code': 'failed',
                'message': get_formatted_error_message(ex, DRFFormatterType.SIMPLE)
            }

    return res

def get_rule_detail(rule_id):
    try:
        # === Dang lam do 23/01/25 ===
        # giai thich duoc flow cua command prefetch below.

        # Rule.camera_configs -> RuleCamera
        prefetch = Prefetch('camera_configs', queryset=RuleCamera.objects.select_related('camera')) # Luu thong tin cua ca RuleCamera + Camera

        rule = Rule.objects.prefetch_related(prefetch).distinct().get(pk=rule_id)

        # rule = Rule.objects.prefetch_related('cameras').distinct().get(pk=rule_id)

    except ObjectDoesNotExist:
        raise module_exceptions.RuleNotFound()

    return rule


def update_rule(rule_id, validated_data, user):
    # add user_id to validated_data
    validated_data['user_id'] = getattr(user, 'id', None)
    user_id = validated_data.pop('user_id', None) or ActorType.SYSTEM
    actor = user_id

    camera_ids = validated_data.pop('camera_configs', None)

    # get rule
    rule = get_rule(rule_id)

    rule.updated_at = timezone.now()
    rule.updated_by = actor

    if validated_data.get('name'):
        rule.name = validated_data.get('name')

    if validated_data.get('type'):
        rule.type = validated_data.get('type')
    
    if validated_data.get('start_time'):
        rule.start_time = validated_data.get('start_time')

    if validated_data.get('end_time'):
        rule.end_time = validated_data.get('end_time')


    # === Update thieu field start, end time, by ... ===

    rule.current_version += 1
    rule.save()

    # 02/02/25
    # Dang lam do: update list Camera cho rule.
    check = False

    if camera_ids:
        list_camera_configs = []

        for cfg in camera_ids:
            # Check - Kiem tra xem id co loi khong ?
            refer_list_camera_id = list(Camera.objects.all().values_list('id', flat=True))

            if cfg not in refer_list_camera_id:
                raise module_exceptions.CameraNotFound(f'Camera {cfg} not found')
            else:
                check = True

        if check:
            rule.camera_configs.all().delete()

            for cfg in camera_ids:
                logger.info(cfg)
                rule_camera = RuleCamera()
                rule_camera.rule_id = rule.id
                rule_camera.camera_id = cfg
                rule_camera.updated_by = actor
                rule_camera.created_by = actor

                list_camera_configs.append(rule_camera)

            RuleCamera.objects.bulk_create(list_camera_configs)

    # === Create new Version to Rule ===
    rule_version = RuleVersion.objects.create(
        rule = rule,
        version_number = rule.current_version,
        name = rule.name,
        type = rule.type,
        start_time = rule.start_time,
        end_time = rule.end_time,
        created_by = actor,
        updated_by = actor
        # thieu created by, ...
    )
    rule_version.save()
    return rule


# === Rule Version ===

def get_list_rule_versions(validated_data):
    # filter rule
    my_filter = Q()

    # cu the version
    version = validated_data.get('version_number')
    if version:
        my_filter &= Q(version_number__icontains=version)


    qs = RuleVersion.objects.select_related('rule').order_by('id')
    # time.sleep(10)
    # logger.info("=============== QS DONEEEEEEE ===========")
    return qs.filter(my_filter)

def get_list_rules(validated_data):
    # filter rule
    my_filter = Q()

    # name
    name = validated_data.get('name')
    if name:
        my_filter &= Q(name__icontains=name)

    # list of rule ids
    list_rule_ids = validated_data.get('rules')
    if list_rule_ids:
        my_filter &= Q(id__in=list_rule_ids)

    qs = Rule.objects.prefetch_related('cameras').order_by('id')

    return qs.filter(my_filter)

def get_rule_version_detail_list(rule_id):

    qs = RuleVersion.objects.select_related('rule').filter(rule_id=rule_id)
    logger.info(qs)
    return qs

def get_rule_version_detail(validated_data, rule_id, version_id):
    # filter rule
    my_filter = Q()

    # version_number
    version_number = validated_data.get('version_number')

    if version_number:
        my_filter &= Q(version_number=version_number)
    # if version_id is not None:
    #     my_filter &= Q(id=version_id)

    qs = RuleVersion.objects.select_related('rule').filter(rule_id=rule_id).filter(id=version_id)
    qs.filter(my_filter)
    logger.info(qs)
    return qs


def remove_rule_version(rule_id, version_id):
    my_filter = Q()

    qs = RuleVersion.objects.select_related('rule').filter(rule_id=rule_id).filter(id=version_id)
    qs.filter(my_filter)
    qs.delete()

def remove_rule_version_with_name(pk, version_number):
    my_filter = Q()
    my_filter &= Q(version_number=version_number)
    qs = RuleVersion.objects.filter(rule_id=pk).filter(my_filter)
    qs.delete()



