import asyncio
import json
import logging
import os
from typing import Any, Dict
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError

logger = logging.getLogger(__name__)


class KafkaProducerService:

    def __init__(self):
        # Reads 'kafka:9092' when running in Docker, defaults to 'localhost:9092'
        self.bootstrap_servers = os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"
        )
        self.producer: AIOKafkaProducer | None = None

    async def start(self):
        """Starts the Kafka producer with automatic connection retry."""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

        # Retry connecting in case Kafka is still initializing in Docker
        while True:
            try:
                logger.info(
                    f"Connecting producer to Kafka at {self.bootstrap_servers}..."
                )
                await self.producer.start()
                logger.info("Kafka Producer successfully started!")
                break
            except KafkaConnectionError:
                logger.warning("Kafka not ready yet. Retrying in 3 seconds...")
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"Error starting Kafka producer: {e}")
                await asyncio.sleep(3)

    async def stop(self):
        """Gracefully stops the producer."""
        if self.producer:
            logger.info("Stopping Kafka Producer...")
            await self.producer.stop()
            logger.info("Kafka Producer stopped.")

    async def send_order(self, topic: str, data: Dict[str, Any]):
        """Sends a message payload to a target topic."""
        if not self.producer:
            raise RuntimeError(
                "Kafka Producer is not initialized. Call start() first."
            )

        try:
            # Send and await confirmation from the broker
            record_metadata = await self.producer.send_and_wait(
                topic, value=data
            )
            logger.info(
                f"Message sent to {record_metadata.topic} "
                f"[partition {record_metadata.partition}] at offset {record_metadata.offset}"
            )
            return record_metadata
        except Exception as e:
            logger.error(f"Failed to produce message: {e}")
            raise e


# Create a global instance to be used across the app
kafka_producer_service = KafkaProducerService()