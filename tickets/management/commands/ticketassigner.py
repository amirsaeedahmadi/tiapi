import logging
from time import sleep

from django.core.management.base import BaseCommand

from tickets.events import TicketAssigned
from tickets.models import Ticket
from tickets.serializers import TicketSerializer
from tickets.services import kafka_event_store

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Assigns tickets to accountable admins"

    def add_arguments(self, parser):
        parser.add_argument("period", type=int)

    def handle(self, *args, period, **options):
        msg = f"Starting to assign tickets every {period} seconds..."
        logger.info(msg)
        while True:
            unassigned_tickets = Ticket.objects.filter(
                status=Ticket.OPEN, accountable=None
            )
            for ticket in unassigned_tickets:
                accountable = ticket.assign()
                if accountable:
                    ticket.refresh_from_db()
                    serializer = TicketSerializer(ticket)
                    event = TicketAssigned(serializer.data)
                    kafka_event_store.add_event(event)

            sleep(period)
