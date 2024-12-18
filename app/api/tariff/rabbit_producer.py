import json
from typing import Any

from app.rabbit.base_producer import BaseProducer
from app.rabbit.models import RoutingKey


class RabbitProducer(BaseProducer):
    async def publish_event(
        self,
        message: dict[str, Any],
        routing_key: RoutingKey,
    ):
        await self.publish(body=json.dumps(message), routing_key=routing_key.value)
