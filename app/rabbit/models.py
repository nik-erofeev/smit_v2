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

    @property
    def get_dsn(self):
        return (
            f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/{self.vhost}"
        )


class DealRmqConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    vhost: str
    exchange_name: str
    queue_name: str
    declare_exchange: bool = True
    exchange_type: ExchangeType = ExchangeType.TOPIC
    durable: bool = True
    arguments: dict | None = None

    @property
    def dsn(self):
        return (
            f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/{self.vhost}"
        )

    def get_exchange_settings(self) -> ExchangeSettings:
        return ExchangeSettings(
            name=self.exchange_name,
            declare=self.declare_exchange,
            type=self.exchange_type,
            durable=self.durable,
            arguments=self.arguments,
        )
