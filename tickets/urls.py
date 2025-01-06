from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import DownloadAttachmentView
from .views import TicketViewSet

router = SimpleRouter()

router.register(r"", TicketViewSet)

urlpatterns = [
    path(
        "attachments/<pk>/download/",
        DownloadAttachmentView.as_view(),
        name="attachment-download",
    ),
]

urlpatterns += router.urls
