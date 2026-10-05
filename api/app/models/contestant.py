from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.age_group import AgeGroup
    from app.models.contestant_field import ContestantField
    from app.models.person import Person
    from app.models.school import School
    from app.models.subcontest import Subcontest

from sqlalchemy import ForeignKeyConstraint, Index
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Contestant(Base):
    __tablename__ = "contestant"
    __table_args__ = (
        ForeignKeyConstraint(
            ["age_group_id"], ["age_group.id"], name="fk_contestant_age_group"
        ),
        ForeignKeyConstraint(["person_id"], ["person.id"], name="fk_contestant_person"),
        ForeignKeyConstraint(["school_id"], ["school.id"], name="fk_contestant_school"),
        ForeignKeyConstraint(
            ["subcontest_id"],
            ["subcontest.id"],
            ondelete="CASCADE",
            name="fk_contestant_subcontest",
        ),
        Index("fk_age_group_idx", "age_group_id"),
        Index("fk_person_idx", "person_id"),
        Index("fk_school_idx", "school_id"),
        Index("fk_subcontest_idx", "subcontest_id"),
        {
            "comment": "Ühel alamvõistlusel osaleja (seotakse tulemus)\n\n"
            "Et inimese omadused (vanusegrupp, kool, juhendajad, ...) võivad "
            "tihti muutuda, siis märkida need pigem siia"
        },
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    subcontest_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    person_id: Mapped[int | None] = mapped_column(INTEGER(11))
    age_group_id: Mapped[int | None] = mapped_column(INTEGER(11))
    school_id: Mapped[int | None] = mapped_column(INTEGER(11))
    placement: Mapped[int | None] = mapped_column(INTEGER(11))

    age_group: Mapped[AgeGroup | None] = relationship(
        "AgeGroup", back_populates="contestant"
    )
    person: Mapped[Person | None] = relationship("Person", back_populates="contestant")
    school: Mapped[School | None] = relationship("School", back_populates="contestant")
    subcontest: Mapped[Subcontest] = relationship(
        "Subcontest", back_populates="contestant"
    )
    mentor: Mapped[list[Person]] = relationship(
        "Person", secondary="mentor", back_populates="contestant_"
    )
    contestant_field: Mapped[list[ContestantField]] = relationship(
        "ContestantField", back_populates="contestant"
    )
