from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.contest import Contest


class Subject(Base):
    __tablename__ = "subject"
    __table_args__: dict[str, str] = {"comment": "Õppeaine - nt. füüsika"}

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)

    contest: Mapped[list[Contest]] = relationship("Contest", back_populates="subject")
