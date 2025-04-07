import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from utils.kafka import create_consumer
from jira.services import jira_service

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = "Starts consuming events and tasks."

    TOPICS = ["Users", "Tickets"]

    CALLBACKS = {
        "CRMTicketCreated": lambda body: jira_service.on_crm_ticket_created(**body),
    }

    def on_message(self, message):
        tp = message.value["type"]
        callback = self.CALLBACKS.get(tp)
        if isinstance(callback, list):
            for clb in callback:
                body = message.value["payload"]
                clb(body)
        elif callback:
            body = message.value["payload"]
            callback(body)

    def handle(self, *args, countdown=3, **options):
        bootstrap_servers = settings.KAFKA_URL
        logger.info("Connecting to Kafka...")
        # Create Kafka consumer
        consumer = create_consumer(bootstrap_servers, "jiraapi", self.TOPICS)
        consumer.start_consuming(on_message=self.on_message)
