from typing import Any

from fastapi import APIRouter, HTTPException
from loguru import logger
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.session_maker import SessionDep

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


@router.get("/check_database", include_in_schema=True)
async def _ready(
    session: AsyncSession = SessionDep,
) -> bool:
    logger.debug("ready")
    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(500, "Database not ready")
    logger.debug("pg ready")

    return True
