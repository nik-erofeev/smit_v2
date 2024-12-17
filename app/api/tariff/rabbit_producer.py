import json
from enum import StrEnum
from typing import Any

from aio_pika import ExchangeType

from app.rabbit.base_producer import BaseProducer
from app.rabbit.models import ExchangeSettings, RmqConfig


class RoutingKey(StrEnum):
    OBJECT_CREATE = "event.created"
    OBJECT_CALCULATE = "event.calculated"
    OBJECT_UPDATE = "event.updated"
    OBJECT_DELETE = "event.deleted"


class RabbitProducer(BaseProducer):
    _EXCHANGE_SETTINGS = ExchangeSettings(
        declare=True,
        name="smit-events",
        type=ExchangeType.TOPIC,
    )

    def __init__(self, rmq_config: RmqConfig, base_vhost: str):
        super().__init__(
            rmq_config=rmq_config,
            exchange_settings=self._EXCHANGE_SETTINGS,
            base_vhost=base_vhost,
        )

    async def publish_event(
        self,
        message: dict[str, Any],
        routing_key: RoutingKey,
    ):
        await self.publish(body=json.dumps(message), routing_key=routing_key.value)
