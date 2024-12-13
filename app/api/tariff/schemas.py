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


class DeleteTariffSchema(BaseModelConfig):
    id: int


class RespDeleteTariffSchema(BaseModelConfig):
    message: str


class UpdateTariffSchema(BaseModelConfig):
    category_type: str | None = Field(
        default=None,
        max_length=20,
        description="Категория тарифа",
    )
    rate: float | None = Field(default=None, ge=0, le=1, description="Рейтинг тарифа")


class UpdateFilterSchema(BaseModelConfig):
    id: int


class UpdateTariffRespSchema(BaseModelConfig):
    message: str = Field(default="Тариф успешно изменен")
    status: str = Field(default="success")
    new_tariff: dict | None = None
