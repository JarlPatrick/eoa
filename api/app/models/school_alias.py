from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.school import School

from sqlalchemy import ForeignKeyConstraint, Index, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SchoolAlias(Base):
    __tablename__ = "school_alias"
    __table_args__ = (
        ForeignKeyConstraint(
            ["correct"],
            ["school.id"],
            ondelete="CASCADE",
            onupdate="CASCADE",
            name="school_alias_correct",
        ),
        Index("idx_school_alias_correct", "correct"),
        Index("name_UNIQUE", "name", unique=True),
    )

    name: Mapped[str] = mapped_column(String(64), primary_key=True)
    correct: Mapped[int | None] = mapped_column(INTEGER(11))

    school: Mapped[School | None] = relationship(
        "School", back_populates="school_alias"
    )
