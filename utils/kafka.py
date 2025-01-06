import json
import logging
import signal
import time

from django.utils import translation
from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka.errors import KafkaError

from utils.json import MessageEncoder

logger = logging.getLogger(__name__)


class Producer:
    def __init__(self, **configs):
        self.producer = KafkaProducer(**configs)

    def on_send_success(self, record_metadata):
        """
        Callback for successful message send.
        """
        msg = (
            f"Message sent successfully to {record_metadata.topic} partition"
            f" {record_metadata.partition} at offset {record_metadata.offset}"
        )
        logger.info(msg)

    def on_send_error(self, exc):
        """
        Callback for failed message send.
        """
        msg = f"Failed to send message: {exc}"
        logger.exception(msg)
        # Optionally, implement retry logic or move message to a dead-letter queue

    def end(self):
        # Make sure all buffered messages are sent before closing
        logger.info("Flushing producer and closing...")
        self.producer.flush()
        self.producer.close()

    def send(self, topic, message, message_key=None):
        """
        Send a message to a Kafka topic.
        """
        try:
            # Asynchronous send with callback
            future = self.producer.send(topic, key=message_key, value=message)
            future.add_callback(self.on_send_success)
            future.add_errback(self.on_send_error)
        except KafkaError as e:
            msg = f"Failed to send message: {e}"
            logger.exception(msg)
            raise
            # Optionally implement retry logic here
        else:
            return future


def create_producer(bootstrap_servers):
    """
    Create and configure a Kafka producer.
    """
    return Producer(
        bootstrap_servers=bootstrap_servers,
        acks="all",  # Wait for leader and all replicas to acknowledge
        retries=5,  # Number of retries for transient errors
        # Ensure this is less than or equal to 5 if idempotence is enabled
        max_in_flight_requests_per_connection=5,
        compression_type="gzip",  # Compress messages for more efficient network usage
        linger_ms=100,  # Delay sending for a short time to batch messages
        batch_size=32 * 1024,  # Batch size in bytes (32 KB)
        # Serialize message value
        value_serializer=lambda v: json.dumps(v, cls=MessageEncoder).encode("utf-8"),
        # Serialize message key
        key_serializer=lambda k: k.encode("utf-8") if k else None,
    )


class Consumer:
    RUNNING = True

    def __init__(self, *topics, **configs):
        self.consumer = KafkaConsumer(*topics, **configs)

    def handle_shutdown_signal(self, signum, frame):
        """
        Signal handler for graceful shutdown on receiving SIGTERM or SIGINT.
        """
        logger.info("Received shutdown signal, stopping consumer...")
        self.RUNNING = False

    def commit_offsets(self):
        """
        Commit offsets manually after processing a batch of messages.
        """
        try:
            self.consumer.commit()
            logger.info("Offsets committed successfully.")
        except Exception as e:
            msg = f"Failed to commit offsets: {e}"
            logger.exception(msg)

    def start_consuming(self, on_message=None):
        # Setup signal handling for graceful shutdown
        signal.signal(signal.SIGTERM, self.handle_shutdown_signal)
        signal.signal(signal.SIGINT, self.handle_shutdown_signal)

        try:
            while self.RUNNING:
                # Poll for new messages
                try:
                    message_batch = self.consumer.poll(timeout_ms=1000)

                    if message_batch:
                        for messages in message_batch.values():
                            for message in messages:
                                try:
                                    # Process each message
                                    msg = f"Processing message: {message.value}"
                                    logger.info(msg)
                                    if on_message:
                                        on_message(message)
                                except Exception as e:
                                    msg = f"Failed to process message: {e}"
                                    logger.exception(msg)
                                    raise
                                    # TODO: We should not raise. We have to move to DLQ
                                    # Optionally, log the offset or take further action

                        # Commit offsets after processing the batch
                        self.commit_offsets()

                except Exception as e:
                    msg = f"Error occurred while consuming messages: {e}"
                    logger.exception(msg)
                    # Sleep to avoid rapid retries in case of recurring errors
                    time.sleep(5)

        finally:
            # Clean up and close the consumer
            logger.info("Closing consumer...")
            self.consumer.close()


def create_consumer(bootstrap_servers, group_id, topics=None):
    """
    Create and configure a Kafka consumer.
    """
    topics = topics or []
    return Consumer(
        *topics,
        bootstrap_servers=bootstrap_servers,
        # Start from the earliest message if no offsets are committed
        auto_offset_reset="earliest",
        # Manually commit offsets, providing control over when a message is
        # considered processed.
        enable_auto_commit=False,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        group_id=group_id,
        auto_commit_interval_ms=5000,  # default is 5000 milliseconds
        max_poll_records=100,  # Number of messages to fetch in one poll
        session_timeout_ms=30000,  # Consumer session timeout
        # Heartbeat to the broker to avoid session timeout
        heartbeat_interval_ms=10000,
    )


class KafkaEventStore:
    def __init__(self, bootstrap_servers):
        self.producer = create_producer(bootstrap_servers)

    def add_event(self, event):
        body = {
            "type": event.name,
            "key": event.key,
            "payload": event.data,
            "timestamp": time.time(),
            "locale": translation.get_language(),
        }
        return self.producer.send(event.topic, body, message_key=event.key)
