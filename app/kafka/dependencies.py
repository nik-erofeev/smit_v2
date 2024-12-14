from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Depends
from loguru import logger

from app.kafka.producer import KafkaProducer


class KafkaProducerManager:
    """
    Класс для управления асинхронным продюсером Kafka.
    """

    def __init__(self, producer: KafkaProducer):
        self.producer = producer

    @asynccontextmanager
    async def create_producer(self) -> AsyncGenerator[KafkaProducer, None]:
        """
        Создаёт и предоставляет новый экземпляр продюсера Kafka.
        Гарантирует остановку продюсера по завершении работы.
        """
        await self.producer.start()
        logger.info("start kafka producer...")
        try:
            yield self.producer
        finally:
            logger.info("stop kafka producer")
            await self.producer.stop()

    async def get_producer(self) -> AsyncGenerator[KafkaProducer, None]:
        """
        Зависимость для FastAPI, возвращающая экземпляр продюсера Kafka.
        """
        async with self.create_producer() as producer:
            yield producer


kafka_producer_manager = KafkaProducerManager(KafkaProducer())
KafkaProducerDep = Depends(kafka_producer_manager.get_producer)
