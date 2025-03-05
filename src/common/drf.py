import logging
import bson
from collections import OrderedDict
from django.apps import apps
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import serializers, exceptions
from rest_framework.pagination import (LimitOffsetPagination as _LimitOffsetPagination,
                                       PageNumberPagination as _PageNumberPagination)
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param

from common.base_model import BaseSimpleModel, BaseModel
from common.enums import ActorType

logger = logging.getLogger('app')


class UserClass:
    def __init__(self, id): # noqa
        self.id = id


def make_mock_object(**kwargs):
    return type("", (object,), kwargs)


def get_object(model_or_queryset, **kwargs):
    """
    Reuse get_object_or_404 since the implementation supports both Model && queryset.
    Catch Http404 & return None
    """
    try:
        return get_object_or_404(model_or_queryset, **kwargs)
    except Http404:
        return None


def create_serializer_class(name, fields):
    return type(name, (serializers.Serializer,), fields)


def inline_serializer(*, fields, data=None, **kwargs):
    serializer_class = create_serializer_class(name="", fields=fields)

    if data is not None:
        return serializer_class(data=data, **kwargs)

    return serializer_class(**kwargs)


def assert_settings(required_settings, error_message_prefix=""):
    """
    Checks if each item from `required_settings` is present in Django settings
    """
    not_present = []
    values = {}

    for required_setting in required_settings:
        if not hasattr(settings, required_setting):
            not_present.append(required_setting)
            continue

        values[required_setting] = getattr(settings, required_setting)

    if not_present:
        if not error_message_prefix:
            error_message_prefix = "Required settings not found."

        stringified_not_present = ", ".join(not_present)

        raise ImproperlyConfigured(f"{error_message_prefix} Could not find: {stringified_not_present}")

    return values


def get_paginated_response(*, pagination_class, serializer_class, queryset, request, view):
    paginator = pagination_class()

    page = paginator.paginate_queryset(queryset, request, view=view)
    logger.info(page)
    if page is not None:

        serializer = serializer_class(page, many=True)
        # logger.info(serializer)
        return paginator.get_paginated_response(serializer.data)

    serializer = serializer_class(queryset, many=True)

    return Response(data=serializer.data)

# === TU VIET ===
# def get_paginated_response(page_size, page_number, queryset, serializer_class):
#     start = (page_number-1) * page_size
#     end = start + page_size
#
#     page_data = queryset[start:end]
#     logger.info(page_data)
#
#     serializers = serializer_class(data = page_data, many = True)
#     serializers.is_valid(raise_exception=True)
#     logger.info(serializers)
#
#     response_data = {
#         "count": len(queryset),
#         "page_size": page_size,
#         "current_page": page_number,
#         "total_pages":(len(queryset) + page_size -1) // page_size,
#         "result": serializers.data,
#     }
#     return Response(data=response_data)


class LimitOffsetPagination(_LimitOffsetPagination):
    default_limit = 10
    max_limit = 50

    def get_paginated_data(self, data):
        return OrderedDict(
            [
                ("limit", self.limit),
                ("offset", self.offset),
                ("count", self.count),
                ("next", self.get_next_link()),
                ("previous", self.get_previous_link()),
                ("results", data),
            ]
        )

    def get_paginated_response(self, data):
        """
        We redefine this method in order to return `limit` and `offset`.
        This is used by the frontend to construct the pagination itself.
        """
        return Response(
            OrderedDict(
                [
                    ("limit", self.limit),
                    ("offset", self.offset),
                    ("count", self.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )


class FastPagination(_LimitOffsetPagination):
    default_limit = 10
    max_limit = 50
    limit = 10
    offset = 0
    is_end_page = False

    def paginate_queryset(self, queryset, request, view=None):  # pragma: no cover
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None

        self.offset = self.get_offset(request)
        self.request = request  # noqa

        # get one extra row
        return list(queryset[self.offset:self.offset + self.limit + 1])

    def get_paginated_response(self, data):
        self.is_end_page = True
        if len(data) == self.limit + 1:
            data = data[:-1]
            self.is_end_page = False

        return Response(
            OrderedDict(
                [
                    ("limit", self.limit),
                    ("offset", self.offset),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )

    def get_next_link(self):
        if self.is_end_page:
            return None

        url = self.request.build_absolute_uri()
        url = replace_query_param(url, self.limit_query_param, self.limit)

        offset = self.offset + self.limit
        return replace_query_param(url, self.offset_query_param, offset)


class PageNumberPagination(_PageNumberPagination):
    page_size_query_param = 'limit'


def model_create(model_class, validated_data, write_db=True):
    # set base model field
    if issubclass(model_class, BaseSimpleModel):
        user_id = validated_data.pop('user_id', None) or ActorType.SYSTEM
        now = timezone.now()
        if issubclass(model_class, BaseModel):
            actor = user_id
        else:
            actor = UserClass(id=user_id)

        validated_data['created_by'] = actor
        validated_data['updated_by'] = actor

        # model.save will auto set created_at, updated_at. This is a backup.
        validated_data['created_at'] = now
        validated_data['updated_at'] = now

    instance = model_class(**validated_data)
    if getattr(instance, 'custom_clean', None):
        instance.custom_clean() # noqa

    if write_db:
        instance.save()
    return instance



def model_update(instance, data, force_updated_fields=None):
    fields = []
    model_class = type(instance)
    if issubclass(model_class, BaseSimpleModel):
        # set base model field
        user_id = data.pop('user_id', None) or ActorType.SYSTEM
        now = timezone.now()
        if issubclass(model_class, BaseModel):
            actor = user_id
        else:
            actor = UserClass(id=user_id)

        setattr(instance, 'updated_by', actor)
        setattr(instance, 'updated_at', now)

        fields = ['updated_by', 'updated_at']

    # check which data fields are modified
    for field, value in data.items():
        # logger.info('FIELDS: %s %s %s' % (field, value, getattr(instance, field)))
        if getattr(instance, field) != value:
            fields.append(field)
            setattr(instance, field, value)

    # Perform an update only if any of the fields was actually changed
    if force_updated_fields:
        fields += force_updated_fields

    if fields:
        if getattr(instance, 'custom_clean', None):
            instance.custom_clean(set(fields))
        # Update only the fields that are meant to be updated.
        # logger.info('UPDATE FIELDS: {} {}'.format(instance.id, fields))
        instance.save(update_fields=fields)

    return instance


class SafeInputModelSerializer(serializers.ModelSerializer):
    def get_validators(self):
        return []

    def include_extra_kwargs(self, kwargs, extra_kwargs):
        super().include_extra_kwargs(kwargs, extra_kwargs)

        kwargs.pop('validators', None)
        return kwargs

    def get_fields(self):
        fields = super().get_fields()
        # remove fields which are managed internally, user must not be updated (read-only fields)
        fields.pop('created_at', None)
        fields.pop('created_by', None)
        fields.pop('updated_at', None)
        fields.pop('updated_by', None)
        fields.pop('deleted_at', None)
        return fields


class ObjectIdField(serializers.CharField):
    def to_representation(self, value):
        return str(value)

    def to_internal_value(self, data):
        if not isinstance(data, str):
            msg = 'Incorrect type. Expected a string, but got %s'
            raise exceptions.ValidationError(msg % type(data).__name__)

        try:
            return bson.ObjectId(data)
        except bson.errors.InvalidId:
            raise exceptions.ValidationError('Object id is invalid')
