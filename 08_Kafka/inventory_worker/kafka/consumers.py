import asyncio
import json
import logging
import os
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError
from config.handlers import OrderHandler

logger = logging.getLogger(__name__)


class InventoryConsumer:
    def __init__(self):
        self.bootstrap_servers = os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"
        )
        self.orders_topic = os.getenv("KAFKA_ORDERS_TOPIC", "orders")
        self.dlq_topic = os.getenv("KAFKA_DLQ_TOPIC", "orders.dlq")
        self.consumer_group = os.getenv(
            "KAFKA_CONSUMER_GROUP", "inventory-service"
        )

        self.consumer: AIOKafkaConsumer | None = None
        self.producer: AIOKafkaProducer | None = None

    async def initialize(self):
        """Connects both the Consumer and the DLQ Producer with retry handling."""
        self.consumer = AIOKafkaConsumer(
            self.orders_topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.consumer_group,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda msg: json.loads(msg.decode("utf-8")),
        )

        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda val: json.dumps(val).encode("utf-8"),
        )

        while True:
            try:
                logger.info("Connecting inventory-worker to Kafka...")
                await self.consumer.start()
                await self.producer.start()
                logger.info("✅ Inventory Worker successfully connected!")
                break
            except KafkaConnectionError:
                logger.warning("Kafka not ready yet. Retrying in 3 seconds...")
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"Unexpected connection error: {e}")
                await asyncio.sleep(3)

    async def send_to_dlq(self, payload: dict, error_message: str):
        """Routes failed order messages to the Dead Letter Queue topic."""
        dlq_payload = {"original_message": payload, "error": error_message}
        try:
            await self.producer.send_and_wait(self.dlq_topic, value=dlq_payload)
            logger.warning(
                f"⚠️ Sent message to DLQ [{self.dlq_topic}]: {error_message}"
            )
        except Exception as err:
            logger.critical(f"🔥 Failed to produce to DLQ: {err}")

    async def start_listening(self):
        """Continuously reads messages from the Kafka topic."""
        if not self.consumer:
            raise RuntimeError(
                "Consumer is not initialized. Run initialize() first."
            )

        try:
            async for msg in self.consumer:
                logger.info(
                    f"Received message from partition {msg.partition} at offset {msg.offset}"
                )
                try:
                    await OrderHandler.process_order(msg.value)
                except Exception as proc_error:
                    logger.error(f"Failed to process message: {proc_error}")
                    await self.send_to_dlq(
                        msg.value, error_message=str(proc_error)
                    )
        finally:
            await self.stop()

    async def stop(self):
        """Closes Kafka connections gracefully."""
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()
        logger.info("Inventory Worker connections closed.")