from enum import Enum, unique

import orjson
import redis.asyncio as aioredis
from loguru import logger

from app.core.settings import RedisConfig


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
        key: str,
        field: str,
        value: dict,
        expire: int | None = None,
    ) -> None:
        try:
            value_bytes = orjson.dumps(value)
            value_str = value_bytes.decode("utf-8")

            await self.connection.hset(key, field, value_str)  # type: ignore
            logger.info(
                f"Set field {field!r} in key {key!r} value {value!r}, expire time {expire}",
            )

            if expire is not None:
                await self.connection.expire(key, expire)
        except aioredis.RedisError as ex:
            logger.error(f"Failed to set field {field!r} in hash {key!r}: {ex}")

    async def get_cache(self, key: str, field: str) -> dict | None:
        try:
            value = await self.connection.hget(key, field)  # type: ignore
            if value:
                return orjson.loads(value)
            return None
        except aioredis.RedisError as ex:
            logger.error(f"Failed to get field {field!r} from hash {key!r}: {ex}")
            return None

    async def del_cache(self, key: str, field: str) -> None:
        try:
            result = await self.connection.hdel(key, field)  # type: ignore
            if result:
                logger.info(f"Deleted field {field!r} from key {key!r}")
            else:
                logger.info(f"Field {field!r} not found in key {key!r}")
        except aioredis.RedisError as ex:
            logger.error(f"Failed to delete field {field!r} from key {key!r}: {ex}")

    async def get_all_cache(self, key: str) -> dict | None:
        try:
            all_data = await self.connection.hgetall(key)  # type: ignore
            if not all_data:
                return None

            # Декодируем ключи и значения
            return {k.decode("utf-8"): orjson.loads(v) for k, v in all_data.items()}
        except aioredis.RedisError as ex:
            logger.error(f"Failed to get all fields from hash {key!r}: {ex}")
            return None
