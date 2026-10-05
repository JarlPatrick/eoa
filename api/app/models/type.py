from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.contest import Contest


class Type(Base):
    __tablename__ = "type"
    __table_args__: dict[str, str] = {
        "comment": "Võistluse tüüp - lahtine, pkv, lv, üleriigiline"
    }

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)

    contest: Mapped[list[Contest]] = relationship("Contest", back_populates="type")
