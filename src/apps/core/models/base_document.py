import mongoengine
from common.enums import ActorType
from ..utils.helpers import utc_now


class BaseDocumentClass:
    created_by = mongoengine.IntField(default=ActorType.SYSTEM)
    updated_by = mongoengine.IntField(default=ActorType.SYSTEM)

    created_at = mongoengine.DateTimeField(default=utc_now)
    updated_at = mongoengine.DateTimeField(default=utc_now)
