import typing

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dao.database import Base

if typing.TYPE_CHECKING:
    from app.models import Blog


class Tag(Base):
    # Название тега
    name: Mapped[str] = mapped_column(String(50), unique=True)

    # Связь Many-to-Many с блогами
    blogs: Mapped[list["Blog"]] = relationship(
        secondary="blog_tags",
        back_populates="tags",  # Указываем промежуточную таблицу
    )
