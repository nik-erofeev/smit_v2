import aio_pika
from aiormq import ChannelNotFoundEntity
from loguru import logger

from app.rabbit.models import ExchangeSettings, RmqConfig


class BaseProducer:
    def __init__(
        self,
        rmq_config: RmqConfig,
        exchange_settings: ExchangeSettings,
        base_vhost: str,
    ):
        self.rmq_config = rmq_config
        self.exchange_settings = exchange_settings
        self.__base_vhost = base_vhost
        self.__connection: aio_pika.Connection | None = None
        self.__channel: aio_pika.Channel | None = None
        self.__exchange: aio_pika.Exchange | None = None

    async def __aenter__(self):
        logger.debug(f"Connecting to RabbitMQ {self.rmq_config.get_dsn}...")
        self.__connection = await aio_pika.connect(url=self.rmq_config.get_dsn)
        self.__channel = await self.__connection.channel()
        self.__exchange = await self.__get_exchange(self.__channel)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        logger.debug("Disconnecting from RabbitMQ...")
        await self.__channel.close()
        self.__channel = None
        await self.__connection.close()
        self.__connection = None
        logger.debug("Successfully disconnected from RabbitMQ.")

    async def __get_exchange(self, channel):
        try:
            exchange = await channel.get_exchange(name=self.exchange_settings.name)
        except ChannelNotFoundEntity as e:
            await channel.reopen()
            # Разрешаем создавать только в нашем vhost
            if (
                self.exchange_settings.declare
                and self.rmq_config.vhost == self.__base_vhost  # noqa: W503
            ):
                exchange = await channel.declare_exchange(
                    name=self.exchange_settings.name,
                    type=self.exchange_settings.type,
                    durable=self.exchange_settings.durable,
                    arguments=self.exchange_settings.arguments,
                )
            else:
                raise e
        return exchange

    async def publish(
        self,
        body: str,
        headers: dict | None = None,
        routing_key: str = "",
    ):
        # Если в контекстном менеджере
        if self.__exchange:
            await self.__publish_message(
                exchange=self.__exchange,
                body=body,
                headers=headers,
                routing_key=routing_key,
            )
        # без контенстного менеджера
        else:
            connection = await aio_pika.connect(url=self.rmq_config.get_dsn)
            async with connection:
                async with connection.channel() as channel:
                    exchange = await self.__get_exchange(channel)
                    await self.__publish_message(
                        exchange=exchange,
                        body=body,
                        headers=headers,
                        routing_key=routing_key,
                    )

    async def __publish_message(
        self,
        exchange: aio_pika.Exchange,
        body: str,
        headers: dict | None = None,
        routing_key: str = "",
    ):
        if not headers:
            headers = {}
        message = aio_pika.Message(
            body=body.encode("utf-8"),
            content_type="application/json",
            headers=headers,
        )

        logger.info(
            f"send message to RabbitMQ\n"
            f"routing_key: {routing_key}\n"
            f"body: {body}\n"
            f"exchange: {exchange}\n"
            f"routing_key: {routing_key}",
        )

        return await exchange.publish(message=message, routing_key=routing_key)
