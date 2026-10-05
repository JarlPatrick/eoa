from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.contestant import Contestant
    from app.models.school_alias import SchoolAlias


class School(Base):
    __tablename__ = "school"
    __table_args__: dict[str, str] = {
        "comment": "Üks kool - nt. TRK\n\nHoida tuleks siiski täisnime"
    }

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)

    school_alias: Mapped[list[SchoolAlias]] = relationship(
        "SchoolAlias", back_populates="school"
    )
    contestant: Mapped[list[Contestant]] = relationship(
        "Contestant", back_populates="school"
    )
