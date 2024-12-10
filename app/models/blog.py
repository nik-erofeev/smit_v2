from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import models
from app.dao.database import Base, str_uniq


class Blog(Base):
    # Заголовок статьи
    title: Mapped[str_uniq]

    # Автор (внешний ключ на таблицу Users)
    author: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Ссылка на объект пользователя
    user: Mapped["models.User"] = relationship("User", back_populates="blogs")

    # Содержание статьи в формате Markdown
    content: Mapped[str] = mapped_column(Text)

    short_description: Mapped[str] = mapped_column(Text)

    # Статус статьи
    status: Mapped[str] = mapped_column(default="published", server_default="published")

    # Связь Many-to-Many с тегами
    tags: Mapped[list["models.Tag"]] = relationship(
        secondary="blog_tags",
        back_populates="blogs",  # Указываем промежуточную таблицу
    )