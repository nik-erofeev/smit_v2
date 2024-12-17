from loguru import logger

from app.redis.redis_client import ExpireTime, RedisClient, RedisKeys


class RedisClientTariff(RedisClient):
    async def cached_tariff(self, tariff_id: int) -> dict | None:
        try:
            cache = await self.get_cache(RedisKeys.TARIFF, str(tariff_id))
            if cache is None:
                logger.debug("Кэш тарифов пуст.")
                return None
            return cache
        except Exception as e:
            logger.error(f"Ошибка при получении кэша тарифов: {e}")
            return None

    async def set_tariff_cache(self, tariff_id: int, tariff_data: dict):
        try:
            tariff_data.pop("id", None)

            await self.set_cache(
                RedisKeys.TARIFF,
                str(tariff_id),
                tariff_data,
                expire=ExpireTime.DAY.value,
            )

        except Exception as e:
            logger.error(f"Ошибка при сохранении тарифа с ID {tariff_id}: {e}")

    async def update_tariff_cache(self, tariff_id: int, new_tariff_data: dict) -> None:
        try:
            existing_data = await self.get_cache(RedisKeys.TARIFF, str(tariff_id))

            if existing_data:
                existing_data.update(new_tariff_data)
                await self.set_cache(
                    RedisKeys.TARIFF,
                    str(tariff_id),
                    existing_data,
                    expire=None,
                )

        except Exception as e:
            logger.error(f"Ошибка при обновлении тарифа с ID {tariff_id}: {e}")

    async def delete_tariff_cache(self, tariff_id: int) -> None:
        try:
            await self.del_cache(RedisKeys.TARIFF, str(tariff_id))

        except Exception as e:
            logger.error(f"Ошибка при удалении тарифа с ID {tariff_id}: {e}")

    async def all_cached_tariffs(self) -> list | None:
        try:
            cache = await self.get_all_cache(RedisKeys.TARIFF)
            if cache is None:
                logger.debug("Кэш тарифов пуст.")
                return None

            return [{**value, "id": int(key)} for key, value in cache.items()]

        except Exception as e:
            logger.error(f"Ошибка при получении кэша тарифов: {e}")
            return None
