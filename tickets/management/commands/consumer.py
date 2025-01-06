import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from tickets.events import FollowUpCreated
from tickets.events import TicketAssigned
from tickets.events import TicketClosed
from tickets.events import TicketCreated
from tickets.models import FollowUp
from tickets.models import Ticket
from users.services import UserService
from utils.kafka import create_consumer

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = "Starts consuming events and tasks."

    TOPICS = ["Users", "Tickets"]

    CALLBACKS = {
        "UserCreated": lambda body: UserService.on_user_created(**body),
        "UserUpdated": lambda body: UserService.on_user_updated(**body),
        "UserDeleted": lambda body: User.objects.filter(pk=body["id"]).delete(),
        TicketCreated.name: lambda body: Ticket.objects.create_ticket(**body),
        TicketAssigned.name: lambda body: Ticket.objects.assign_ticket(
            body["id"], accountable=body["accountable"]
        ),
        TicketClosed.name: lambda body: Ticket.objects.filter(pk=body["id"]).update(
            status=Ticket.CLOSED
        ),
        FollowUpCreated.name: lambda body: FollowUp.objects.create_followup(**body),
    }

    def on_message(self, message):
        tp = message.value["type"]
        callback = self.CALLBACKS.get(tp)
        if callback:
            body = message.value["payload"]
            callback(body)

    def handle(self, *args, countdown=3, **options):
        bootstrap_servers = settings.KAFKA_URL
        logger.info("Connecting to Kafka...")
        # Create Kafka consumer
        consumer = create_consumer(bootstrap_servers, "ticketingapi", self.TOPICS)
        consumer.start_consuming(on_message=self.on_message)
