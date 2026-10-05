from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.age_group import AgeGroup
    from app.models.contest import Contest
    from app.models.contestant import Contestant
    from app.models.subcontest_column import SubcontestColumn

from sqlalchemy import ForeignKeyConstraint, Index, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Subcontest(Base):
    __tablename__ = "subcontest"
    __table_args__ = (
        ForeignKeyConstraint(
            ["age_group_id"], ["age_group.id"], name="fk_subcontest_age_group"
        ),
        ForeignKeyConstraint(
            ["contest_id"],
            ["contest.id"],
            ondelete="CASCADE",
            name="fk_subcontest_contest",
        ),
        Index("fk_age_group_idx", "age_group_id"),
        Index("fk_contest_idx", "contest_id"),
        {
            "comment": "Üks eraldi arvestusega võistlus - nt. lahtise noorem rühm, lv 12. "
            "klass"
        },
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    contest_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    age_group_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    tasks_link: Mapped[str | None] = mapped_column(String(128))
    solutions_link: Mapped[str | None] = mapped_column(String(128))
    description: Mapped[str | None] = mapped_column(String(1024))

    age_group: Mapped[AgeGroup] = relationship("AgeGroup", back_populates="subcontest")
    contest: Mapped[Contest] = relationship("Contest", back_populates="subcontest")
    contestant: Mapped[list[Contestant]] = relationship(
        "Contestant", back_populates="subcontest"
    )
    subcontest_column: Mapped[list[SubcontestColumn]] = relationship(
        "SubcontestColumn", back_populates="subcontest"
    )
