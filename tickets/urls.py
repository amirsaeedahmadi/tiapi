from django.urls import path

from .views import TicketViewSet

# from  import JiraTicketUpdateHook  # 👈 Import from jira app

ticket_list = TicketViewSet.as_view({"get": "list", "post": "create"})
ticket_detail = TicketViewSet.as_view({"get": "retrieve"})
comment_list = TicketViewSet.as_view({"get": "fetch_comments", "post": "create_comments"})
download_attachment = TicketViewSet.as_view({"get": "download_attachment"})

urlpatterns = [
    path("", ticket_list, name="ticket-list"),
    path("<int:ticket_id>/", ticket_detail, name="ticket-detail"),
    path("<int:ticket_id>/comments/", comment_list, name="comment-list"),
    path("attachments/<int:attachment_id>/<str:filename>/", download_attachment, name="download-attachment"),
    # path(
    #     "tickets/comment_creation_webhook",
    #     JiraTicketUpdateHook.as_view({"post": "comment_created"}),
    #     name="comment_creation_webhook",
    # ),
]
