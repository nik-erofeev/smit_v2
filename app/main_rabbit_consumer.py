import asyncio

from loguru import logger

from app.core.settings import APP_CONFIG
from app.kafka.dependencies import kafka_producer
from app.rabbit.example_cunsumer import ExampleConsumer


async def start_consumer():
    async with kafka_producer:
        consumer_rabbit = ExampleConsumer(
            consumer_config=APP_CONFIG.consumer,
            kafka_producer=kafka_producer,
        )
        await consumer_rabbit.consume_messages()


# или без with
# async def start_consumer():
#     await kafka_producer.start()
#     try:
#         await consumer_rabbit.consume_messages()
#     finally:
#         await kafka_producer.stop()


if __name__ == "__main__":
    try:
        asyncio.run(start_consumer())
    except KeyboardInterrupt:
        logger.info("Consumer stopped.")
