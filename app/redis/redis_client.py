from datetime import date
from enum import Enum, unique
from typing import TypeVar

import orjson
import redis.asyncio as aioredis
from loguru import logger

from app.core.settings import RedisConfig

RedisKey = TypeVar("RedisKey", bytes, str, memoryview)
RedisValue = TypeVar("RedisValue", bytes, memoryview, str, int, float, dict, date)


class ExpireTime(Enum):
    # Время жизни ключа в секундах
    DAY = 86400  # 60 * 60 * 24
    SIX_HOURS = 21600  # 60 * 60 * 6
    TEN_HOURS = 36000  # 60 * 60 * 10
    TWELVE_HOURS = 43200  # 60 * 60 * 12
    WEEK = 604800  # 60 * 60 * 24 * 7


@unique
class RedisKeys(str, Enum):
    TARIFF = "tariff-data"
    EXAMPLE = "example-data"


class RedisClient:
    def __init__(self, config: RedisConfig) -> None:
        self._config = config
        self._redis_pool: aioredis.Redis | None = None
        self._next_retry_connect: float | None = None

    @property
    def connection(self) -> aioredis.Redis:
        if not self._redis_pool:
            self.reconnect()

        return self._redis_pool  # type: ignore

    def connect(self) -> None:
        redis_pool = aioredis.ConnectionPool.from_url(
            url=self._config.host,
            encoding="utf8",
        )

        self._redis_pool = aioredis.Redis(
            connection_pool=redis_pool,
            socket_keepalive=True,
            single_connection_client=True,
            socket_timeout=60,
        )

    async def close(self) -> None:
        logger.info("REDIS: Closing...")
        await self.connection.close()

    async def health_check(self) -> bool:
        conn = self.connection
        if conn is None:
            logger.error("REDIS: No connection available for health check")
            return False
        return await conn.ping()

    async def setup(self) -> None:
        self.connect()
        if await self.health_check():
            logger.debug(f"Redis client connected to {self._config.host}")
        else:
            logger.error(f"REDIS: Connection error {self._config.host}")
            raise aioredis.ConnectionError

    def reconnect(self) -> None:
        logger.info("REDIS: Reconnecting...")
        self.connect()

    async def set_cache(
        self,
        key: RedisKey,
        value: RedisValue,
        expire: int | None = None,
    ) -> None:
        try:
            if not isinstance(value, bytes):
                value = orjson.dumps(value, option=orjson.OPT_NON_STR_KEYS)  # type: ignore

            await self.connection.set(key, value, ex=expire)  # type: ignore
            logger.info(f"Set key {key!r} cache with expiration time {expire} seconds")
        except aioredis.RedisError as ex:
            logger.error(f"Failed to set cache for key {key!r}: {ex}")

    async def get_cache(self, key: RedisKey) -> dict | None:
        try:
            cache = await self.connection.get(key)
            if cache:
                return orjson.loads(cache)
            return None
        except aioredis.RedisError as ex:
            logger.error(f"Failed to get cache for key {key!r}: {ex}")
            return None
