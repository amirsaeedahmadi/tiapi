import logging
from jira.services.jira import JiraService

from utils.kafka import KafkaEventStore
from django.conf import settings


logger = logging.getLogger(__name__)
bootstrap_servers = settings.KAFKA_URL
kafka_event_store = KafkaEventStore(bootstrap_servers=bootstrap_servers)


jira_service = JiraService(kafka_event_store)
