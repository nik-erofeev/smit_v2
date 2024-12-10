from datetime import datetime
from typing import Annotated, Any

from sqlalchemy import func, Integer, TIMESTAMP
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncAttrs,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column

from app.core.settings import APP_CONFIG

engine = create_async_engine(
    url=str(APP_CONFIG.db.sqlalchemy_db_uri),
    echo=APP_CONFIG.db.echo,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # todo: обязательно False
)

str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
    )

    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"

    def to_dict(self) -> dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        """Строковое представление объекта для удобства отладки."""
        return f"<{self.__class__.__name__}(id={self.id}, created_at={self.created_at}, updated_at={self.updated_at})>"
