from rest_framework.viewsets import ViewSet
import re
from jira.serializers.ticket_serializer import (
    JiraIssueAttachmentSerializer,
    JiraIssueSerializer,
)
from jira.services import jira_service
from loguru import logger


class JiraTicketUpdateHook(ViewSet):
    # permission_classes = [IsAuthenticated]

    def comment_created(self, request):
        logger.info(f"{request.data=}")
        comment_data = request.data
        comment_text = comment_data["body"]
        attachment_regex_patterns = [
            r"[^!\n]*!(?P<attachment_name>[^!|]+)\|?[^\!\|]*![^\!\n]*",
            r"[^\[\]\n]*\[\^(?P<attachment_name>[^\[\]]*)\][^\[\]\n]*",
        ]
        attachment_names = []
        attachments_data = []
        for attachment_pattern in attachment_regex_patterns:
            for match in re.finditer(pattern=attachment_pattern, string=comment_text):
                attachment_names.append(match.group("attachment_name"))
        ticket_data = jira_service.fetch_ticket_detail(request.data["issueId"])
        ticket_serializer = JiraIssueSerializer(data=ticket_data)
        ticket_serializer.is_valid(raise_exception=True)
        for attachment in JiraIssueAttachmentSerializer(
            instance=ticket_serializer.validated_data["attachments"], many=True
        ):
            attachment_data = attachment.validated_data
            if attachment_data["filename"] in attachment_names:
                attachments_data.append(
                    {
                        "name": attachment_data["filename"],
                        "author_email": attachment_data["author"]["emailAddress"],
                        "download-link": attachment_data["content"],
                    }
                )

        ticket_panel_id = ticket_serializer.validated_data["panel_id"]
        comment_data["ticket_id"] = ticket_panel_id
        comment_data["attachments_data"] = attachments_data
        jira_service.add_comment_created(comment_data)
        return comment_data
