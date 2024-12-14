from fastapi import Depends

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


kafka_producer_manager = KafkaProducerManager(KafkaProducer())
KafkaProducerDep = Depends(kafka_producer_manager.get_producer)
