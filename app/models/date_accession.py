from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from app.dao.database import Base

if TYPE_CHECKING:
    from app.models import Tariff


class DateAccession(Base):
    __tablename__ = "date_accessions"  # type: ignore

    # todo: created_at вместо published_at
    tariffs: Mapped["Tariff"] = relationship(
        "Tariff",
        back_populates="date_accession",
        cascade="all, delete-orphan",
    )
