from datetime import date

from fastapi import APIRouter, Body, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.tariff.dao import TariffDAO
from app.api.tariff.example_descriptions import add_tariff_request_example
from app.api.tariff.schemas import (
    CreateTariffRespSchema,
    RespDeleteTariffSchema,
    TariffRespSchema,
    TariffSchema,
)
from app.core.settings import APP_CONFIG
from app.dao.session_maker import TransactionSessionDep

router = APIRouter(
    prefix=APP_CONFIG.api.v1,
    tags=["Тарифы"],
)


@router.post(
    "/tariff",
    summary="Добавить тариф",
    response_model=list[CreateTariffRespSchema],
    response_class=ORJSONResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_tariff(
    tariff_data: dict[date, list[TariffSchema]] = Body(
        ...,
        example=add_tariff_request_example,
    ),
    session: AsyncSession = TransactionSessionDep,
):
    return await TariffDAO.create_tariff(session=session, tariff_data=tariff_data)


@router.get(
    "tariff/{tariff_id}",
    response_model=TariffRespSchema,
    response_class=ORJSONResponse,
    status_code=status.HTTP_200_OK,
)
async def get_tariff(tariff_id: int, session: AsyncSession = TransactionSessionDep):
    return await TariffDAO.get_tariff_by_id(
        tariff_id=tariff_id,
        session=session,
    )


@router.delete(
    "tariff/{tariff_id}",
    response_model=RespDeleteTariffSchema,
    response_class=ORJSONResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_tariff(tariff_id: int, session: AsyncSession = TransactionSessionDep):
    return await TariffDAO.delete_tariff_by_id(tariff_id, session)
