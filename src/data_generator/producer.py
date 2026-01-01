"""Kafka producer for publishing pageview events to Kafka."""

import json
import time
from typing import Any

from kafka import KafkaProducer
from kafka.errors import KafkaError, NoBrokersAvailable

from src.common.config import PipelineConfig
from src.common.logging import setup_logging
from src.common.metrics import events_published, publish_errors, start_metrics_server
from src.data_generator.generator import PageviewGenerator


class PageviewProducer:
    """Kafka producer for publishing pageview events.

    Attributes:
        config: Pipeline configuration
        logger: Logger instance
        producer: Kafka producer instance
        topic: Kafka topic name
    """

    def __init__(self, config: PipelineConfig):
        """Initialize the Kafka producer.

        Args:
            config: Pipeline configuration
        """
        self.config = config
        self.logger = setup_logging("pageview-producer", config.log_level)
        self.topic = config.kafka_topic

        self.logger.info(
            f"Initializing Kafka producer on {config.kafka_bootstrap_servers}",
            topic=self.topic,
        )

        max_retries = 10
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=config.kafka_bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    acks="all",  # Wait for all replicas to acknowledge
                    retries=3,
                    max_in_flight_requests_per_connection=1,  # Preserve ordering
                    compression_type="gzip",  # Compress messages
                )
                self.logger.info("Kafka producer initialized successfully")
                return
            except NoBrokersAvailable:
                if attempt < max_retries - 1:
                    self.logger.warning(
                        f"Kafka not ready yet (Attempt {attempt + 1}/{max_retries}). Retrying in {retry_delay}s..."
                    )
                    time.sleep(retry_delay)
                else:
                    self.logger.error("Max retries reached. Kafka brokers not available.")
                    raise
            except KafkaError as e:
                self.logger.error("Failed to initialize Kafka producer", error=str(e))
                raise

    def publish(self, event: dict[str, Any]) -> None:
        """Publish a single event to Kafka.

        Args:
            event: Pageview event dictionary

        Raises:
            KafkaError: If publish fails after retries
        """
        try:
            future = self.producer.send(self.topic, value=event)
            # Block until sent (with timeout)
            record_metadata = future.get(timeout=10)

            events_published.inc()
            self.logger.debug(
                "Event published",
                user_id=event["user_id"],
                partition=record_metadata.partition,
                offset=record_metadata.offset,
            )
        except KafkaError as e:
            publish_errors.inc()
            self.logger.error("Failed to publish event", user_id=event.get("user_id"), error=str(e))
            raise

    def run(self) -> None:
        """Run the producer continuously."""
        self.logger.info("Starting event generation", rate=f"{self.config.event_rate} events/sec")

        generator = PageviewGenerator()
        count = 0

        try:
            for event in generator.generate_stream(rate=self.config.event_rate):
                self.publish(event)
                count += 1
                if count == 1:
                    self.logger.info("First event published successfully!")
                if count % 100 == 0:
                    self.logger.info(f"Progress check: Published {count} events...")
        except KeyboardInterrupt:
            self.logger.info("Shutting down producer...")
        except Exception as e:
            self.logger.error("Producer error", error=str(e))
            raise
        finally:
            self.producer.flush()
            self.producer.close()
            self.logger.info("Producer shutdown complete")


def main() -> None:
    """Main entry point for the data generator."""
    config = PipelineConfig()

    # Start metrics server
    start_metrics_server(config.metrics_port)

    producer = PageviewProducer(config)
    producer.run()


if __name__ == "__main__":
    main()
