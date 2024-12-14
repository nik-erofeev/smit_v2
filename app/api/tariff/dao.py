from datetime import date

from fastapi import HTTPException
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.tariff.schemas import (
    CreateTariffRespSchema,
    DeleteTariffSchema,
    RespDeleteTariffSchema,
    TariffRespSchema,
    TariffSchema,
)
from app.dao.base import BaseDAO
from app.models import DateAccession, Tariff


class TariffDAO(BaseDAO):
    model = Tariff

    @classmethod
    async def create_tariff(
        cls,
        session: AsyncSession,
        tariff_data: dict[date, list[TariffSchema]],
    ) -> list[CreateTariffRespSchema]:
        response_tariffs = []
        for created_at, tariffs in tariff_data.items():
            try:
                date_accession_model = DateAccession(created_at=created_at)
                session.add(date_accession_model)
                await session.flush()

                for tariff in tariffs:
                    tariff_model = cls.model(
                        category_type=tariff.category_type,
                        rate=tariff.rate,
                        date_accession_id=date_accession_model.id,
                    )

                    session.add(tariff_model)

                    # todo: если через базовую add
                    # insert_tariff = CreateTariffSchema(
                    #     **tariff.model_dump(), date_accession_id=date_accession_model.id
                    # )
                    # await cls.add(session, insert_tariff)

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

            except SQLAlchemyError as e:
                logger.error(f"Database error occurred while adding tariff: {e=!r}")
                raise HTTPException(status_code=500, detail="Ошибка базы данных")

            except ValueError as e:
                logger.error(f"Invalid data provided for tariff creation{e=!r}.")
                raise HTTPException(status_code=400, detail=str(e))

        logger.info(f"Created {len(response_tariffs)} tariffs successfully.")
        return response_tariffs

    @classmethod
    async def get_tariff_by_id(
        cls,
        tariff_id: int,
        session: AsyncSession,
    ) -> TariffRespSchema:
        result = await cls.find_one_or_none_by_id(
            data_id=tariff_id,
            session=session,
        )
        if not result:
            raise HTTPException(status_code=404, detail="Тариф не найден")

        # todo: если __repr__  3 полей объявлен Base + .to_dict
        # result_dict = result.to_dict()
        # return TariffRespSchema.model_validate(result_dict)
        return TariffRespSchema.model_validate(result)

    @classmethod
    async def delete_tariff_by_id(
        cls,
        tariff_id: int,
        session: AsyncSession,
    ) -> RespDeleteTariffSchema:
        tariff = await cls.find_one_or_none_by_id(tariff_id, session)

        # # через новый запрос
        # query = select(cls.model).filter_by(id=tariff_id)
        # result = await session.execute(query)
        # tariff = result.scalar_one_or_none()

        if not tariff:
            logger.warning(f"Tariff with id {tariff_id} not found.")
            raise HTTPException(status_code=404, detail="Тариф не найден")

        try:
            delete_tariff = DeleteTariffSchema(id=tariff_id)
            await cls.delete(session=session, filters=delete_tariff)

            # # через новый запрос
            # await session.delete(tariff)
            # await session.flush()

            logger.info(f"Tariff with ID {tariff_id} has been deleted successfully.")
            return RespDeleteTariffSchema(
                message=f"Tariff with ID {tariff_id} has been deleted.",
            )
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Ошибка базы данных")
