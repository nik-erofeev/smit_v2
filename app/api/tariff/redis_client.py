import orjson
from loguru import logger

from app.redis.redis_client import ExpireTime, RedisClient, RedisKeys


class RedisClientTariff(RedisClient):
    async def get_tariff_cache(self) -> dict[int, dict] | None:
        try:
            cache = await self.get_cache(RedisKeys.TARIFF)
            if cache:
                return {int(tariff_id): tariff for tariff_id, tariff in cache.items()}
            logger.debug("Кэш тарифов пуст.")
            return None

        except Exception as e:
            logger.error(f"Ошибка при получении кэша тарифов: {e}")
            return None

    async def set_tariff_cache(self, value: dict[int, dict]):
        try:
            current_cache = await self.get_tariff_cache() or {}
            current_cache.update(value)

            cache = orjson.dumps(current_cache, option=orjson.OPT_NON_STR_KEYS)
            await self.set_cache(RedisKeys.TARIFF, cache, expire=ExpireTime.DAY.value)
            logger.info(f"Кэш успешно обновлен: {value}")

        except Exception as e:
            logger.error(f"Ошибка при обновлении кэша тарифов: {e}")
