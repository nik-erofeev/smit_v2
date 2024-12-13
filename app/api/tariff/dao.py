from datetime import date

from fastapi import HTTPException
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.tariff.schemas import TariffResponseSchema, TariffSchema
from app.dao.base import BaseDAO
from app.models import DateAccession, Tariff


class TariffDAO(BaseDAO):
    model = Tariff

    @classmethod
    async def create_tariff(
        cls,
        session: AsyncSession,
        tariff_data: dict[date, list[TariffSchema]],
    ) -> list[TariffResponseSchema]:
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

                response_tariffs.append(
                    TariffResponseSchema(
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
