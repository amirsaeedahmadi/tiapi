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
from jira.services import JiraService
from django.conf import settings

User = get_user_model()


class TicketService:
    def __init__(self, event_store):
        self.event_store = event_store
        self.jira_service = JiraService(event_store=event_store) if settings.JIRA_ENABLED else None

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
        attachment_ids = kwargs.pop("attachment_ids", [])
        kwargs["id"] = uuid.uuid4()
        ticket_instance = Ticket.objects.create(**kwargs)

        serialized_ticket = self.serialize(ticket_instance)

        try:
            jira_issue = self.jira_service.create_jira_issue(
                project=self.jira_service.base_project,
                description=ticket_instance.description,
                issue_type=self.jira_service.base_issue_type,
                summary=ticket_instance.subject,
                customer_id=ticket_instance.user.id,
                panel_id="optional_panel_id",  # adjust as needed
                priority=ticket_instance.priority
            )
        except Exception as e:
            pass

        self.event_store.add_event("TicketCreated", serialized_ticket)
        return ticket_instance
        # attachment_ids = kwargs.pop("attachment_ids")
        # pk = uuid.uuid4()
        # instance = Ticket(
        #     pk=pk,
        #     **kwargs,
        # )
        # data = self.serialize(instance)
        # data["attachments"] = attachment_ids
        # event = TicketCreated(data)
        # self.event_store.add_event(event)
        # return instance

    @staticmethod
    def on_ticket_created(**kwargs):
        if kwargs["cat"] == Ticket.TECHNICAL:
            pass
            # TODO: jira
        else:
            pass
            Ticket.objects.create_ticket(**kwargs)

    @staticmethod
    def on_followup_created(**kwargs):
        if kwargs["cat"] == Ticket.TECHNICAL:
            pass
            # TODO: jira
        else:
            pass
            FollowUp.objects.create_followup(**kwargs)

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


ticket_service = TicketService(kafka_event_store)
