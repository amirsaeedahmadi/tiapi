import json
import logging

from django.contrib.auth import get_user_model
from django.db import IntegrityError

from .serializers import WritableUserSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


class UserService:
    @staticmethod
    def on_user_created(**kwargs):
        serializer = WritableUserSerializer(data=kwargs)
        if not serializer.is_valid():
            msg = f"User cannot be created: {json.dumps(serializer.errors)}"
            logger.warning(msg)
            return
        try:
            User.objects.create(**serializer.validated_data)
        except IntegrityError as e:
            msg = f"IntegrityError: {kwargs['email']} - {e!s}"
            logger.warning(msg)

    @staticmethod
    def on_user_updated(**kwargs):
        pk = kwargs.pop("id")
        instance = User.objects.get(pk=pk)
        serializer = WritableUserSerializer(instance, data=kwargs, partial=True)
        serializer.is_valid()
        if not serializer.is_valid():
            msg = f"User cannot be updated: {json.dumps(serializer.errors)}"
            logger.warning(msg)
            return None
        return serializer.save()
