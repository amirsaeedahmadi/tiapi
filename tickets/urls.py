from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import DownloadAttachmentView, TicketViewSet
# from  import JiraTicketUpdateHook  # 👈 Import from jira app

router = SimpleRouter()
router.register(r"", TicketViewSet)

urlpatterns = [
    path(
        "attachments/<pk>/download/",
        DownloadAttachmentView.as_view(),
        name="attachment-download",
    ),
    # path(
    #     "tickets/comment_creation_webhook",
    #     JiraTicketUpdateHook.as_view({"post": "comment_created"}),
    #     name="comment_creation_webhook",
    # ),
]

urlpatterns += router.urls
