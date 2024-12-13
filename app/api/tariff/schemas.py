from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class BaseModelConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TariffSchema(BaseModelConfig):
    category_type: str = Field(max_length=20, description="Категория тарифа")
    rate: float = Field(ge=0, le=1, description="Рейтинг тарифа")


class TariffResponseSchema(BaseModel):
    id: int
    created_at: date
    tariffs: list[TariffSchema]
