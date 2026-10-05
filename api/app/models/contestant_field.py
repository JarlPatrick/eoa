from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKeyConstraint, Index, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.contestant import Contestant
    from app.models.subcontest_column import SubcontestColumn


class ContestantField(Base):
    __tablename__ = "contestant_field"
    __table_args__ = (
        ForeignKeyConstraint(
            ["contestant_id"],
            ["contestant.id"],
            ondelete="CASCADE",
            name="fk_contestant_field_contestant",
        ),
        ForeignKeyConstraint(
            ["task_id"],
            ["subcontest_column.id"],
            ondelete="CASCADE",
            name="fk_contestant_field_task",
        ),
        Index("fk_contestant_points_1_idx", "contestant_id"),
        {"comment": "Ühe võistleja üks väli vastavalt subcontest_column'ile"},
    )

    task_id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    contestant_id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    entry: Mapped[str] = mapped_column(String(64), nullable=False)

    contestant: Mapped[Contestant] = relationship(
        "Contestant", back_populates="contestant_field"
    )
    task: Mapped[SubcontestColumn] = relationship(
        "SubcontestColumn", back_populates="contestant_field"
    )
