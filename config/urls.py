# ruff: noqa
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Ticketing API",
        default_version="v1",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = i18n_patterns(
    path("tickets/admin/", admin.site.urls),
    path(
        "tickets/api-docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="swagger-schema-ui",
    ),
    path("tickets/", include("tickets.urls")),
)
