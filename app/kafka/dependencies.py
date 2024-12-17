from fastapi import Depends

from app.core.settings import APP_CONFIG
from app.kafka.producer import KafkaProducer


class KafkaProducerManager:
    """
    Класс для управления асинхронным продюсером Kafka.
    """

    def __init__(self, producer: KafkaProducer):
        self.producer = producer

    async def get_producer(self) -> KafkaProducer:
        """
        Зависимость для FastAPI, возвращающая экземпляр продюсера Kafka.
        """
        return self.producer


kafka_producer = KafkaProducer(
    APP_CONFIG.kafka.bootstrap_servers,
    APP_CONFIG.kafka.topik,
)
kafka_producer_manager = KafkaProducerManager(kafka_producer)

KafkaProducerDep = Depends(kafka_producer_manager.get_producer)

# если хотим каждый раз получать новый коннект к Kafka (а не держать постоянный)
# todo: +убрать из lifespan kafka_producer.start() / kafka_producer.stop()


# async def get_kafka_producer() -> AsyncGenerator[KafkaProducer, None]:
#     await kafka_producer.start()
#     try:
#         logger.debug("Starting Kafka producer...")
#         yield kafka_producer
#         logger.debug("Stopping Kafka producer...")
#     finally:
#         await kafka_producer.stop()
#
#
# KafkaProducerDep = Depends(get_kafka_producer)
