from datetime import date

from fastapi import APIRouter, Body, File, Query, status, UploadFile
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.tariff.dao import TariffDAO
from app.api.tariff.example_descriptions import add_tariff_request_example
from app.api.tariff.schemas import (
    CalculateCostResponseSchema,
    CalculateCostSchema,
    CreateTariffRespSchema,
    RespDeleteTariffSchema,
    TariffRespSchema,
    TariffSchema,
    UpdateTariffRespSchema,
    UpdateTariffSchema,
)
from app.core.settings import APP_CONFIG
from app.dao.session_maker import TransactionSessionDep
from app.kafka.dependencies import KafkaProducerDep
from app.kafka.producer import KafkaProducer

router = APIRouter(
    prefix=f"{APP_CONFIG.api.v1}/tariffs",
    tags=["Тарифы"],
)


@router.post(
    "/",
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
    producer: KafkaProducer = KafkaProducerDep,
):
    return await TariffDAO.create_tariff(
        session=session,
        tariff_data=tariff_data,
        producer=producer,
    )


@router.post(
    "/calculate",
    summary="Страховая стоимость",
    response_model=CalculateCostResponseSchema,
    response_class=ORJSONResponse,
    status_code=status.HTTP_200_OK,
)
async def calculate_cost(
    data: CalculateCostSchema,
    session: AsyncSession = TransactionSessionDep,
    producer: KafkaProducer = KafkaProducerDep,
):
    return await TariffDAO.calculate_cost(data, session, producer)


@router.post("/upload")
async def upload_tariffs(
    file: UploadFile = File(...),
    session: AsyncSession = TransactionSessionDep,
    producer: KafkaProducer = KafkaProducerDep,
):
    return await TariffDAO.upload_tariffs(session, producer, file)


@router.get(
    "/{tariff_id}",
    summary="Получить тариф",
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
    "/{tariff_id}",
    summary="Удалить тариф",
    response_model=RespDeleteTariffSchema,
    response_class=ORJSONResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_tariff(
    tariff_id: int,
    session: AsyncSession = TransactionSessionDep,
    producer: KafkaProducer = KafkaProducerDep,
):
    return await TariffDAO.delete_tariff_by_id(tariff_id, session, producer)


@router.get(
    "/",
    summary="Получить список тарифов",
    response_model=list[TariffRespSchema],
    response_class=ORJSONResponse,
    status_code=status.HTTP_200_OK,
)
async def get_all_tariffs(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(10, ge=10, le=100, description="Записей на странице"),
    session: AsyncSession = TransactionSessionDep,
):
    return await TariffDAO.get_all_tariffs(page, page_size, session)


@router.patch(
    "/{tariff_id}",
    summary="Обновить тариф",
    response_model=UpdateTariffRespSchema,
    response_class=ORJSONResponse,
    status_code=status.HTTP_200_OK,
)
async def update_tariff(
    tariff_id: int,
    new_tariff: UpdateTariffSchema,
    session: AsyncSession = TransactionSessionDep,
    producer: KafkaProducer = KafkaProducerDep,
):
    return await TariffDAO.update_tariff(tariff_id, new_tariff, session, producer)
