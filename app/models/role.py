import typing

from sqlalchemy.orm import Mapped, relationship

from app.dao.database import Base, str_uniq

if typing.TYPE_CHECKING:
    from app.models import User


class Role(Base):
    name: Mapped[str_uniq]
    users: Mapped[list["User"]] = relationship("User", back_populates="role")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"
