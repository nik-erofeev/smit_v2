from fastapi import Depends

from app.api.tariff.redis_client import RedisClientTariff
from app.core.settings import APP_CONFIG


class RedisClientTariffManager:
    """
    Класс для управления клиентом Redis для тарифов.
    """

    def __init__(self, redis_client: RedisClientTariff):
        self.redis_client = redis_client

    async def get_client(self) -> RedisClientTariff:
        """
        Зависимость для FastAPI, возвращающая экземпляр клиента RedisTariff.
        """
        return self.redis_client


redis_cli = RedisClientTariff(APP_CONFIG.redis)

redis_manager = RedisClientTariffManager(redis_cli)
RedisClientTariffDep = Depends(redis_manager.get_client)


# если хотим каждый раз получать новый коннект к Redis (а не держать постоянный)! :todo: +убрать из lifespan redis_cli.setup() / redis_cli.close()
# async def get_redis_client() -> AsyncGenerator[RedisClientTariff, None]:
#     await redis_cli.setup()
#     try:
#         logger.debug("Starting Redis client...")
#         yield redis_cli
#         logger.debug("Closing Redis client...")
#     finally:
#         await redis_cli.close()
#
#
# RedisClientTariffDep = Depends(get_redis_client)
