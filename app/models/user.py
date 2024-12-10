import typing

from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dao.database import Base, str_uniq

if typing.TYPE_CHECKING:  # type: ignore
    from app.models import Blog, Role


class User(Base):
    phone_number: Mapped[str_uniq]
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str_uniq]
    password: Mapped[str]
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id"),
        default=1,
        server_default=text("1"),
    )
    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="users",
        lazy="joined",
    )
    blogs: Mapped[list["Blog"]] = relationship(
        "Blog",
        back_populates="user",  # Должно совпадать с именем в модели Blogs
    )

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"
