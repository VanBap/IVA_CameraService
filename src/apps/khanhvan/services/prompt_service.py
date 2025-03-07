import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q, Subquery, OuterRef
from django.forms import IntegerField

from common.enums import ActorType
from ..models.prompt import Prompt
from ..utils import exceptions as module_exceptions

logger = logging.getLogger('app')

def get_list_prompts(validated_data):
    qs = Prompt.objects.all()
    # filter
    p_id = validated_data.get('prompt_id')
    if p_id:
        qs = qs.filter(id=p_id)

    return qs

@transaction.atomic
def create_prompt(validated_data, user):
    validated_data['user_id'] = getattr(user, 'id', None)
    user_id = validated_data.pop('user_id', None) or ActorType.SYSTEM

    actor_id = user_id
    validated_data['created_by'] = actor_id
    validated_data['updated_by'] = actor_id

    prompt = Prompt(**validated_data)
    prompt.save()

    return prompt

def get_prompt(prompt_id):
    try:
        prompt = Prompt.objects.get(pk=prompt_id)

    except ObjectDoesNotExist:
        raise module_exceptions.NotFound()

    return prompt

def remove_prompt(prompt_id):
    prompt=get_prompt(prompt_id)
    prompt.delete()
