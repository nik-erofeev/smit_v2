from collections.abc import AsyncGenerator

from fastapi import Depends

from app.api.tariff.rabbit_producer import RabbitProducer
from app.core.settings import APP_CONFIG

rabbit_producer = RabbitProducer(
    rmq_config=APP_CONFIG.rabbit,
    base_vhost=APP_CONFIG.rabbit.vhost,
)


async def get_rabbit_producer() -> AsyncGenerator[RabbitProducer, None]:
    async with rabbit_producer as producer:
        yield producer


RabbitProducerDep = Depends(get_rabbit_producer)
