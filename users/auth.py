import logging

from django.conf import settings
from django.contrib.auth.backends import ModelBackend as _ModelBackend
from rest_framework_simplejwt.authentication import (
    JWTAuthentication as _JWTAuthentication,
)

logger = logging.getLogger(__name__)


class ModelBackend(_ModelBackend):
    def get_permission_list(self, user_obj):
        return user_obj.access_list + user_obj.roles

    def has_perm(self, user_obj, perm, obj=None):
        return (
            user_obj.is_active
            and user_obj.is_staff
            and (user_obj.is_superuser or perm in self.get_permission_list(user_obj))
        )


class JWTAuthentication(_JWTAuthentication):
    def authenticate(self, request):
        refresh_token = request.COOKIES.get(settings.REFRESH_TOKEN_COOKIE_NAME)
        if not refresh_token:
            return None

        raw_token = request.COOKIES.get(settings.ACCESS_TOKEN_COOKIE_NAME)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
