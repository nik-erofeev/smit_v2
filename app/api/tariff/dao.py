import asyncio
import json
from datetime import date

from fastapi import File, HTTPException, UploadFile
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.tariff.rabbit_producer import RabbitProducer, RoutingKey
from app.api.tariff.redis_client import RedisClientTariff
from app.api.tariff.schemas import (
    CalculateCostResponseSchema,
    CalculateCostSchema,
    CategoryTypeSchema,
    CreateTariffRespSchema,
    CreateTariffSchema,
    DeleteTariffSchema,
    RespDeleteTariffSchema,
    TariffRespSchema,
    TariffSchema,
    UpdateFilterSchema,
    UpdateTariffRespSchema,
    UpdateTariffSchema,
)
from app.api.tariff.utils import ActionType, create_message
from app.dao.base import BaseDAO
from app.kafka.producer import KafkaProducer
from app.models import DateAccession, Tariff


class TariffFileProcessor:
    @staticmethod
    def process_file(contents: bytes) -> dict[date, list[TariffSchema]]:
        try:
            data = json.loads(contents)
            tariffs = {}
            for date_str, tariff_list in data.items():
                created_at = date.fromisoformat(date_str)
                tariff_objects = [TariffSchema(**tariff) for tariff in tariff_list]
                tariffs[created_at] = tariff_objects
                logger.info(
                    f"Processed rates for date {created_at}: {tariff_objects}",
                )
            return tariffs

        except json.JSONDecodeError:
            logger.exception("Invalid JSON format.")
            raise HTTPException(status_code=400, detail="Invalid JSON format")

        except Exception as e:
            logger.exception(f"An error occurred while processing the file: {e}")
            raise HTTPException(
                status_code=500,
                detail="An error occurred while processing the file",
            )


class TariffDAO(BaseDAO):
    model = Tariff

    @classmethod
    async def create_tariff(
        cls,
        session: AsyncSession,
        tariff_data: dict[date, list[TariffSchema]],
        kafka: KafkaProducer,
        rabbit: RabbitProducer,
    ) -> list[CreateTariffRespSchema]:
        response_tariffs = []
        for created_at, tariffs in tariff_data.items():
            try:
                date_accession_model = DateAccession(created_at=created_at)
                session.add(date_accession_model)
                await session.flush()

                # # todo: если добавлять по 1 тарифу
                # for tariff in tariffs:
                #     tariff_model = cls.model(
                #         category_type=tariff.category_type,
                #         rate=tariff.rate,
                #         date_accession_id=date_accession_model.id,
                #     )
                #
                #     session.add(tariff_model)
                #
                #     # todo: если добавлять через базовую Base.add
                #     # insert_tariff = CreateTariffSchema(
                #     #     **tariff.model_dump(), date_accession_id=date_accession_model.id
                #     # )
                #     # await cls.add(session, insert_tariff)

                # для add_many создаем список
                tariff_models = [
                    CreateTariffSchema(
                        **tariff.model_dump(),
                        date_accession_id=date_accession_model.id,
                    )
                    for tariff in tariffs
                ]

                # Добавляем через  add_many для загрузки списка
                await cls.add_many(session, tariff_models)

                response_tariffs.append(
                    CreateTariffRespSchema(
                        id=date_accession_model.id,
                        created_at=created_at,
                        tariffs=tariffs,
                    ),
                )
                logger.info(
                    f"Successfully created tariffs for published_at {created_at}.",
                )
                message = create_message(
                    action=ActionType.CREATE_TARIFF,
                    date_accession_id=date_accession_model.id,
                    updated_at=str(date_accession_model.updated_at),
                )

                # запускаем параллельно
                await asyncio.gather(
                    kafka.send_message(message),
                    rabbit.publish_event(
                        message=message,
                        routing_key=RoutingKey.OBJECT_CREATE,
                    ),
                )

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred while adding tariff: {e=!r}")
                raise HTTPException(status_code=500, detail="Ошибка базы данных")

            except ValueError as e:
                logger.error(f"Invalid data provided for tariff creation{e=!r}.")
                raise HTTPException(status_code=400, detail=str(e))

        logger.info(f"Created {len(response_tariffs)} tariffs successfully.")
        return response_tariffs

    @classmethod
    async def upload_tariffs(
        cls,
        session: AsyncSession,
        kafka: KafkaProducer,
        rabbit: RabbitProducer,
        file: UploadFile = File(...),
    ):
        contents = await file.read()
        tariffs_data = TariffFileProcessor.process_file(contents)
        logger.info(f"Tariff file {file.filename} uploaded and processed.")
        return await cls.create_tariff(session, tariffs_data, kafka, rabbit)

    @classmethod
    async def get_tariff_by_id(
        cls,
        tariff_id: int,
        session: AsyncSession,
        redis: RedisClientTariff,
    ) -> TariffRespSchema:
        # Проверяем кеш в редисе. Если есть возвращаем из кеша
        cache = await redis.cached_tariff(tariff_id)
        if cache:
            return TariffRespSchema(id=tariff_id, **cache)

        result = await cls.find_one_or_none_by_id(
            data_id=tariff_id,
            session=session,
        )

        if not result:
            raise HTTPException(status_code=404, detail="Тариф не найден")

        # todo: если __repr__  3 полей объявлен Base + .to_dict
        # result_dict = result.to_dict()
        # return TariffRespSchema.model_validate(result_dict)

        tariff = TariffRespSchema.model_validate(result)
        # пишем в редис
        await redis.set_tariff_cache(tariff_id, tariff.model_dump())

        return tariff

    @classmethod
    async def get_all_tariffs(
        cls,
        page: int,
        page_size: int,
        session: AsyncSession,
    ):
        result = await cls.paginate(
            session=session,
            page=page,
            page_size=page_size,
            filters=None,
        )
        return [TariffRespSchema.model_validate(tariff) for tariff in result]

    @classmethod
    async def delete_tariff_by_id(
        cls,
        tariff_id: int,
        session: AsyncSession,
        kafka: KafkaProducer,
        rabbit: RabbitProducer,
        redis: RedisClientTariff,
    ) -> RespDeleteTariffSchema:
        tariff = await cls.find_one_or_none_by_id(tariff_id, session)

        # # через новый запрос
        # query = select(cls.model).filter_by(id=tariff_id)
        # result = await session.execute(query)
        # tariff = result.scalar_one_or_none()

        if not tariff:
            logger.info(f"Tariff with id {tariff_id} not found.")
            raise HTTPException(status_code=404, detail="Тариф не найден")

        try:
            delete_tariff = DeleteTariffSchema(id=tariff_id)
            # await cls.delete(session=session, filters=delete_tariff)  # todo: в geather можно

            # # через новый запрос
            # await session.delete(tariff)
            # await session.flush()

            logger.info(f"Tariff with ID {tariff_id} has been deleted successfully.")

            message = create_message(
                action=ActionType.DELETE_TARIFF,
                date_accession_id=tariff.date_accession_id,
                tariff_id=tariff_id,
            )

            # запускаем параллельно
            await asyncio.gather(
                cls.delete(session=session, filters=delete_tariff),
                kafka.send_message(message),
                rabbit.publish_event(
                    message=message,
                    routing_key=RoutingKey.OBJECT_DELETE,
                ),
                redis.delete_tariff_cache(tariff_id),
            )

            return RespDeleteTariffSchema(
                message=f"Tariff with ID {tariff_id} has been deleted.",
            )
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Ошибка базы данных")

    @classmethod
    async def update_tariff(
        cls,
        tariff_id: int,
        new_tariff: UpdateTariffSchema,
        session: AsyncSession,
        kafka: KafkaProducer,
        rabbit: RabbitProducer,
        redis: RedisClientTariff,
    ) -> UpdateTariffRespSchema:
        filters = UpdateFilterSchema(id=tariff_id)
        result = await cls.update(session, filters, new_tariff)

        # без наследования
        # query = select(cls.model).filter_by(id=tariff_id)
        # result = await session.execute(query)
        # tariff = result.scalar_one_or_none()

        # if not tariff:
        if not result:
            logger.info(f"Tariff with ID {tariff_id} not found.")
            raise HTTPException(status_code=404, detail="Тариф не найден")

        # без наследования (продолжение)
        # tariff_dict = new_tariff.model_dump(exclude_unset=True)
        # query_2 = (
        #     update(cls.model).where(cls.model.id == tariff_id).values(**tariff_dict)
        # )
        #
        # try:
        #     await session.execute(query_2)
        #
        # except SQLAlchemyError as e:
        #     await session.rollback()
        #     logger.error(f"Ошибка при обновлении записей: {e}")
        #     raise e
        # без наследования (конец)

        message = create_message(
            action=ActionType.UPDATE_TARIFF,
            tariff_id=tariff_id,
            new_tariff=new_tariff.model_dump(),
        )

        # Запускаем  параллельно
        await asyncio.gather(
            redis.update_tariff_cache(tariff_id, new_tariff.model_dump()),
            kafka.send_message(message),
            rabbit.publish_event(
                message=message,
                routing_key=RoutingKey.OBJECT_UPDATE,
            ),
        )

        return UpdateTariffRespSchema(
            new_tariff=new_tariff.model_dump(exclude_none=True),
        )

    @classmethod
    async def calculate_cost(
        cls,
        data: CalculateCostSchema,
        session: AsyncSession,
        kafka: KafkaProducer,
        rabbit: RabbitProducer,
    ):
        # пример через фильтр модели
        tariff = await cls.find_one_or_none(
            session=session,
            filters=CategoryTypeSchema(id=data.tariff_id),
        )

        # так же по id базового
        # tariff = await cls.find_one_or_none_by_id(data.tariff_id, session)

        if not tariff:
            logger.info(f"Tariff {data.tariff_id}. not found")
            raise HTTPException(
                status_code=404,
                detail=f"Rate not found for the {data.tariff_id}",
            )

        insurance_cost = data.declared_value * tariff.rate
        logger.info(
            f"Insurance cost calculated: {insurance_cost} for declared value: {data.declared_value} and rate: {tariff.rate}.",
        )

        message = create_message(
            ActionType.CALCULATE_INSURANCE_COST,
            tariff.date_accession_id,
            str(tariff.updated_at),
            data.tariff_id,
        )

        # Запускаем  параллельно
        await asyncio.gather(
            kafka.send_message(message),
            rabbit.publish_event(
                message=message,
                routing_key=RoutingKey.OBJECT_CALCULATE,
            ),
        )

        return CalculateCostResponseSchema(
            tariff_id=data.tariff_id,
            declared_value=data.declared_value,
            rate=tariff.rate,
            insurance_cost=insurance_cost,
        )
