from collections.abc import Awaitable, Callable

import aio_pika
from aiormq import ChannelNotFoundEntity
from loguru import logger

from app.rabbit.models import RmqConfig


class BaseConsumer:
    def __init__(
        self,
        rmq_config: RmqConfig,
        # fmt: off
        on_message: None
        | (Callable[[aio_pika.IncomingMessage], Awaitable[bool]]) = None,
        # fmt: on
        routing_key: str | None = "",
    ):
        self.rmq_config = rmq_config
        self.routing_key = routing_key
        self.on_message = on_message
        self.connection: aio_pika.Connection | None = None
        self.channel: aio_pika.Channel | None = None
        self.exchange: aio_pika.Exchange | None = None
        self.queue: aio_pika.Queue | None = None

    async def __aenter__(self):
        self.connection = await aio_pika.connect(url=self.rmq_config.get_dsn)
        self.channel = await self.connection.channel()
        self.exchange = await self._get_exchange()
        self.queue = await self._declare_queue()
        await self._bind_queue()
        await self.queue.consume(self._handle_message)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._close_resources()

    async def _get_exchange(self):
        try:
            return await self.channel.get_exchange(name=self.rmq_config.exchange_name)
        except ChannelNotFoundEntity:
            await self.channel.reopen()
            if self.rmq_config.exchange_declare:
                return await self.channel.declare_exchange(
                    name=self.rmq_config.exchange_name,
                    type=self.rmq_config.exchange_type,
                    durable=self.rmq_config.exchange_durable,
                    arguments=self.rmq_config.exchange_arguments,
                )
            raise

    async def _declare_queue(self):
        return await self.channel.declare_queue(
            self.rmq_config.queue_name,
            durable=True,
        )

    async def _handle_message(self, message: aio_pika.IncomingMessage):
        if self.on_message:
            success = await self._process_message(message)
            await self._ack_or_nack_message(message, success)
        else:
            logger.error("No on_message callback provided.")
            raise RuntimeError("No on_message callback provided.")

    async def _process_message(self, message: aio_pika.IncomingMessage) -> bool:
        if self.on_message is None:
            logger.error("on_message callback is not set.")
            return False  # Возвращаем False, если on_message не задан

        try:
            result = await self.on_message(message)
            return result is True  # Обработка случая, когда результат может быть None
        except Exception as e:
            logger.error(f"Exception occurred while handling message: {e}")
            return False

    async def _ack_or_nack_message(
        self,
        message: aio_pika.IncomingMessage,
        success: bool,
    ):
        if success:
            await self._ack_message(message)
        else:
            await self._nack_message(message)

    @staticmethod
    async def _ack_message(message: aio_pika.IncomingMessage):
        try:
            await message.ack()
            logger.info("Message acknowledged.")
        except Exception as e:
            logger.error(f"Failed to acknowledge message: {e!r}")

    @staticmethod
    async def _nack_message(message: aio_pika.IncomingMessage):
        try:
            await message.nack(requeue=True)
            logger.info("Message negatively acknowledged.")
        except Exception as e:
            logger.error(f"Failed to negatively acknowledge message: {e!r}")

    async def _bind_queue(self):
        await self.queue.bind(exchange=self.exchange, routing_key=self.routing_key)

    async def _close_resources(self):
        if self.channel:
            await self.channel.close()
            logger.info("Channel closed successfully.")
        if self.connection:
            await self.connection.close()
            logger.info("Connection closed successfully.")
