from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import models
from app.dao.database import Base


class Tag(Base):
    # Название тега
    name: Mapped[str] = mapped_column(String(50), unique=True)

    # Связь Many-to-Many с блогами
    blogs: Mapped[list["models.Blog"]] = relationship(
        secondary="blog_tags",
        back_populates="tags",  # Указываем промежуточную таблицу
    )
