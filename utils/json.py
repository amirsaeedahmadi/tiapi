from uuid import UUID

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.functional import Promise


class MessageEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return str(obj)
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, UUID):
            return obj.hex
        return super().default(obj)
