from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.contestant_field import ContestantField
    from app.models.subcontest import Subcontest

from sqlalchemy import ForeignKeyConstraint, Index, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SubcontestColumn(Base):
    __tablename__ = "subcontest_column"
    __table_args__ = (
        ForeignKeyConstraint(
            ["subcontest_id"],
            ["subcontest.id"],
            ondelete="CASCADE",
            name="fk_task_subcontest",
        ),
        Index("fk_subcontest_idx", "subcontest_id"),
        {
            "comment": "Üks näidatav tulp (ülesanne, kogupunktid, järk) iga võistleja "
            "jaoks\n\n"
            "seq_no määrab, mitmendana seda tulpa näitama peaks"
        },
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    subcontest_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    seq_no: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    extra: Mapped[str | None] = mapped_column(String(64))

    subcontest: Mapped[Subcontest] = relationship(
        "Subcontest", back_populates="subcontest_column"
    )
    contestant_field: Mapped[list[ContestantField]] = relationship(
        "ContestantField", back_populates="task"
    )
