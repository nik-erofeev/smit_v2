from enum import StrEnum

from aio_pika import ExchangeType
from pydantic import BaseModel


class ExchangeSettings(BaseModel):
    name: str
    declare: bool = (
        False  # True создает эксчендж при его отсутствии, но только в vhost проекта
    )
    type: ExchangeType = ExchangeType.FANOUT
    durable: bool = True
    arguments: dict | None = None


class RmqConfig(BaseModel):
    host: str = ""
    port: int = 5672
    user: str = ""
    password: str = ""
    vhost: str = ""

    exchange_name: str = ""  # todo имя передать
    exchange_declare: bool = (
        True  # True создает эксчендж при его отсутствии, но только в vhost проекта
    )
    exchange_type: ExchangeType = ExchangeType.TOPIC
    exchange_durable: bool = True
    exchange_arguments: dict | None = None

    queue_name: str = ""

    @property
    def get_dsn(self):
        return (
            f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/{self.vhost}"
        )


class RoutingKey(StrEnum):
    OBJECT_CREATE = "event.created"
    OBJECT_CALCULATE = "event.calculated"
    OBJECT_UPDATE = "event.updated"
    OBJECT_DELETE = "event.deleted"
