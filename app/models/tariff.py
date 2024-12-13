from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dao.database import Base

if TYPE_CHECKING:
    from app.models import DateAccession


class Tariff(Base):
    category_type: Mapped[str] = mapped_column(String(32))
    rate: Mapped[float] = mapped_column(Float)
    date_accession_id: Mapped[int] = mapped_column(
        ForeignKey("date_accessions.id", ondelete="CASCADE"),
        nullable=False,
    )

    date_accession: Mapped["DateAccession"] = relationship(
        "DateAccession",
        back_populates="tariffs",
    )
