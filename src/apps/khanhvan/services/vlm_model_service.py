import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q, Subquery, OuterRef
from django.forms import IntegerField

from common.enums import ActorType
from ..models.vlm_model import VLMModel
from ..utils import exceptions as module_exceptions

logger = logging.getLogger('app')


def get_list_ai_models(validated_data):
    qs = VLMModel.objects.all()
    # filter
    name = validated_data.get('name')
    if name:
        qs = qs.filter(name__icontains=name)

    return qs

@transaction.atomic
def create_ai_model(validated_data, user):
    validated_data['user_id'] = getattr(user, 'id', None)
    user_id = validated_data.pop('user_id', None) or ActorType.SYSTEM

    actor_id = user_id
    validated_data['created_by'] = actor_id
    validated_data['updated_by'] = actor_id

    aimodel = VLMModel(**validated_data)
    aimodel.save()

    return aimodel

def get_vlm_model(vlm_model_id):
    try:
        vlm_model_id = VLMModel.objects.get(pk=vlm_model_id)

    except ObjectDoesNotExist:
        raise module_exceptions.VlmModelNotFound()

    return vlm_model_id

def remove_vlm_model(vlm_model_id):
    vlmmodel = get_vlm_model(vlm_model_id)

    # update yeu cau thong bao user xoa rule
    check_rule = vlmmodel.rules.first()
    if check_rule:
        raise module_exceptions.CannotRemoveModel(f'Rule id {check_rule.id}, {check_rule.name} is using this model')
    else:
        vlmmodel.delete()
