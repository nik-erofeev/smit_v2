from typing import Any

from fastapi import APIRouter
from loguru import logger

router = APIRouter(
    tags=["default"],
)


@router.get("/ping", include_in_schema=True)
async def _ping() -> str:
    logger.debug("ping")
    return "pong"


@router.get("/exception", include_in_schema=True)
async def _exception() -> Any:
    """Роутер для отправки триггеров в sentry и ТГ
    (если переданы креды в env)"""
    try:
        return 1 / 0
    except ZeroDivisionError as e:
        logger.error(f"Use exception {e=!r}")


# todo дописать
# @router.get("/ready", include_in_schema=False)
# async def _ready() -> bool:
#     logger.debug("ready")
#     try:
#         logger.debug("testing db")
#         async with self._db.get_session() as session:
#             await session.execute(text("SELECT 1"))
#     except SQLAlchemyError:
#         raise HTTPException(500, "Database not ready")
#     logger.debug("pg ready")
#
#     return True
