from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.contestant import Contestant
    from app.models.subcontest import Subcontest

from sqlalchemy import String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AgeGroup(Base):
    __tablename__ = "age_group"

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    min_class: Mapped[int | None] = mapped_column(INTEGER(11))
    max_class: Mapped[int | None] = mapped_column(INTEGER(11))

    subcontest: Mapped[list[Subcontest]] = relationship(
        "Subcontest", back_populates="age_group"
    )
    contestant: Mapped[list[Contestant]] = relationship(
        "Contestant", back_populates="age_group"
    )
