from typing import Any

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import ORJSONResponse
from loguru import logger
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.default.schemas import DBResponse, ExcResponse, PingResponse
from app.dao.session_maker import SessionDep

router = APIRouter(
    tags=["default"],
)


@router.get(
    "/ping",
    include_in_schema=True,
    response_model=PingResponse,
    response_class=ORJSONResponse,
    summary="Проверка работоспособности сервера",
    status_code=status.HTTP_200_OK,
)
async def _ping():
    logger.debug("ping")
    return PingResponse(message="pong")


@router.get(
    "/exception",
    include_in_schema=True,
    response_model=ExcResponse,
    response_class=ORJSONResponse,
    summary="Отправка ecx в sentry и ТГ",
    status_code=status.HTTP_200_OK,
)
async def _exception() -> Any:
    """Роутер для отправки триггеров в sentry и ТГ
    (если переданы креды в env)"""
    try:
        return 1 / 0
    except ZeroDivisionError as e:
        logger.error(f"Use exception {e=!r}")
        return ExcResponse(
            message="Ошибка отправлена в sentry и ТГ (если переданы креды)",
        )


@router.get(
    "/check_database",
    include_in_schema=True,
    response_model=DBResponse,
    response_class=ORJSONResponse,
    summary="Проверка доступности базы данных",
    status_code=status.HTTP_200_OK,
)
async def _ready(session: AsyncSession = SessionDep):
    logger.debug("ready")
    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(500, "Database not ready")

    logger.debug("pg ready")
    return DBResponse(status="Database is ready")
