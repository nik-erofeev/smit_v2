from datetime import datetime

from pydantic import BaseModel, computed_field, ConfigDict, Field


class BaseModelConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BlogCreateSchemaBase(BaseModelConfig):
    title: str
    content: str
    short_description: str
    tags: list[str] = []


class BlogCreateSchemaAdd(BlogCreateSchemaBase):
    author: int


class UserBase(BaseModelConfig):
    id: int
    first_name: str
    last_name: str


class TagResponse(BaseModelConfig):
    id: int
    name: str


class BlogFullResponse(BaseModelConfig):
    id: int
    author: int
    title: str
    content: str
    short_description: str
    created_at: datetime
    status: str
    tags: list[TagResponse]
    # Это поле нужно для работы computed fields, но оно не будет включено в финальный JSON
    user: UserBase = Field(exclude=True)

    # Используем вычисляемые поля для преобразования данных о пользователе
    @computed_field  # type: ignore[misc]
    @property
    def author_id(self) -> int | None:
        return self.user.id if self.user else None

    @computed_field  # type: ignore[misc]
    @property
    def author_name(self) -> str | None:
        if self.user:
            return f"{self.user.first_name} {self.user.last_name}"
        return None


class BlogNotFind(BaseModel):
    message: str
    status: str


class CreateBlogResponse(BaseModel):
    status: str = Field(default="success")
    message: str


class BlogListResponse(BaseModel):
    page: int
    total_page: int
    total_result: int
    blogs: list[BlogFullResponse]


class DeleteBlogResponse(BaseModel):
    status: str
    message: str
