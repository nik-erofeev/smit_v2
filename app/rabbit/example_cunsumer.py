import asyncio
import json

import aio_pika
from loguru import logger

from app.kafka.producer import KafkaProducer
from app.rabbit.base_concumer import BaseConsumer
from app.rabbit.models import RmqConfig


class ExampleConsumer(BaseConsumer):
    def __init__(
        self,
        consumer_config: RmqConfig,
        kafka_producer: KafkaProducer,
    ):
        super().__init__(
            rmq_config=consumer_config,
            on_message=self.process_message,
            # routing_key="#",  # все routing_key
            # routing_key="event.#",  # все routing_key, начинающиеся с "event."
            routing_key="event.*",  # все routing_key, начинающиеся с "event." и имеющие один сегмент после
        )
        self.kafka_producer = kafka_producer

    async def process_message(self, message: aio_pika.IncomingMessage) -> bool:
        try:
            body = json.loads(message.body.decode())
            return await self._process_event(body)
        except Exception as e:
            logger.error(f"Failed to process message: {e!r}")
            return False

    async def _process_event(self, body: dict) -> bool:
        """Обрабатываем сообщение и отправляем в кафку в новый топик"""
        try:
            new_body = {"action": body.get("action"), "rmq": "ack"}
            if "tariff_id" in body:
                new_body["tariff_id"] = body["tariff_id"]

            await self.kafka_producer.send_message(new_body, "rmq_new_topic")
            logger.info(f"Message {new_body} successfully sent to Kafka.")
            return True
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            return False

    async def consume_messages(self):
        async with self:
            logger.debug(f"Consumer started. {self.rmq_config.get_dsn}")
            await asyncio.Event().wait()
