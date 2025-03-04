import uuid
import logging

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from tickets.events import FollowUpCreated
from tickets.events import TicketAssigned
from tickets.events import TicketClosed
from tickets.events import TicketCreated
from tickets.models import FollowUp
from tickets.models import Ticket
from tickets.serializers import ReadOnlyFollowUpSerializer
from tickets.serializers import ReadOnlyTicketSerializer
from utils.decorators import delay_return
from utils.kafka import kafka_event_store
from utils.jira import JiraClient
from django.conf import settings


logger = logging.getLogger(__name__)

User = get_user_model()


class TicketService:
    def __init__(self, event_store):
        self.event_store = event_store
        self.jira_client = JiraClient() if settings.JIRA_ENABLED else None

    @staticmethod
    def serialize(instance):
        serializer = ReadOnlyTicketSerializer(instance)
        return serializer.data

    @staticmethod
    def serialize_followup(instance):
        serializer = ReadOnlyFollowUpSerializer(instance)
        data = serializer.data.copy()
        if data["user"] == str(instance.ticket.user.pk):
            data["audience"] = "admin"
        else:
            data["audience"] = "user"
        return data

    @delay_return()
    def create(self, **kwargs):
        attachment_ids = kwargs.pop("attachment_ids")
        pk = uuid.uuid4()
        instance = Ticket(
            pk=pk,
            **kwargs,
        )
        data = self.serialize(instance)
        data["attachments"] = attachment_ids
        event = TicketCreated(data)
        self.event_store.add_event(event)
        return instance

    @delay_return()
    def assign(self, instance, accountable):
        exclude_kwargs = {"pk": instance.accountable.pk} if instance.accountable else {}
        can_assign = (
            User.objects.get_assignable_admins(exclude_kwargs=exclude_kwargs)
            .filter(pk=accountable.pk)
            .first()
        )
        if not can_assign:
            raise ValidationError({"detail": _("This is not what we want.")})
        instance.accountable = accountable
        data = self.serialize(instance)
        event = TicketAssigned(data)
        self.event_store.add_event(event)
        return instance

    def close(self, instance):
        if instance.status == Ticket.CLOSED:
            raise ValidationError({"detail": _("Ticket already closed.")})
        instance.status = Ticket.CLOSED
        data = self.serialize(instance)
        event = TicketClosed(data)
        self.event_store.add_event(event)
        return instance

    def add_followup(self, **kwargs):
        attachment_ids = kwargs.pop("attachment_ids")
        instance = FollowUp(pk=uuid.uuid4(), **kwargs)
        data = self.serialize_followup(instance)
        data["attachments"] = attachment_ids
        event = FollowUpCreated(data)
        self.event_store.add_event(event)
        return instance
    
    def create_jira_issue(self, ticket):
        if not self.jira_client or not settings.JIRA_ENABLED:
            return None
            
        try:
            response = self.jira_client.create_issue(
                project_key="DRVG",
                summary=ticket.subject,
                description=ticket.description,
                issue_type_id="10100"
            )
            
            if response and 'key' in response:
                # You might want to store the Jira key with the ticket
                # This would require adding a jira_key field to the Ticket model
                return response
                
        except Exception as e:
            logger.error(f"Failed to create Jira issue for ticket {ticket.id}: {str(e)}")
            
        return None


ticket_service = TicketService(kafka_event_store)
