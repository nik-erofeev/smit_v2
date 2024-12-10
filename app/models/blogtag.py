from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.dao.database import Base


# Промежуточная таблица для связи Many-to-Many
class BlogTag(Base):
    __tablename__ = "blog_tags"  # type: ignore

    # Внешние ключи
    blog_id: Mapped[int] = mapped_column(
        ForeignKey("blogs.id", ondelete="CASCADE"),
        nullable=False,
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Уникальное ограничение для пары blog_id и tag_id
    __table_args__ = (UniqueConstraint("blog_id", "tag_id", name="uq_blog_tag"),)
