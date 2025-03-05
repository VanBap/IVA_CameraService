import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q, Subquery, OuterRef
from django.forms import IntegerField

from common.enums import ActorType
from ..models.ai_model import AImodel
from ..utils import exceptions as module_exceptions

logger = logging.getLogger('app')


def get_list_ai_models(validated_data):
    qs = AImodel.objects.all()
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

    aimodel = AImodel(**validated_data)
    aimodel.save()

    return aimodel