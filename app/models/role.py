from sqlalchemy.orm import Mapped, relationship

from app import models
from app.dao.database import Base, str_uniq


class Role(Base):
    name: Mapped[str_uniq]
    users: Mapped[list["models.User"]] = relationship(back_populates="role")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, name={self.name})"
