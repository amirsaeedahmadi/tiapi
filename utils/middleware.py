import logging

from django.conf import settings
from django.db import connection
from rest_framework import status

logger = logging.getLogger(__name__)


class DbQueryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        num = f"\x1b[6;30;42m{len(connection.queries)} queries\x1b[0m"
        logger.info(num)
        logger.info(connection.queries)

        return response


class AdminHostMiddleware:
    """
    Middleware to set the current app mode based on the request's hostname.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.is_admin_host = False
        if request.get_host() in settings.ADMIN_ALLOWED_HOSTS:
            request.is_admin_host = True
        return self.get_response(request)


class DeleteCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            for cookie in request.COOKIES:
                response.delete_cookie(cookie)

        return response
