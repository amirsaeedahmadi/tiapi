from django.urls import path
from .views import JiraTicketUpdateHook

urlpatterns = [
    path(
        "tickets/comment_creation_webhook",
        JiraTicketUpdateHook.as_view({"post": "comment_created"}),
        name="comment_creation_webhook",
    ),
]
