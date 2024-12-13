from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseModelConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TariffSchema(BaseModelConfig):
    category_type: str = Field(max_length=20, description="Категория тарифа")
    rate: float = Field(ge=0, le=1, description="Рейтинг тарифа")


class CreateTariffRespSchema(BaseModel):
    id: int
    created_at: date
    tariffs: list[TariffSchema]


class CreateTariffSchema(TariffSchema):  # todo: если через базовую .add
    date_accession_id: int


class TariffRespSchema(BaseModelConfig):
    id: int
    category_type: str
    rate: float
    created_at: datetime
    date_accession_id: int
