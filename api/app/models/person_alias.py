from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKeyConstraint, Index, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.person import Person


class PersonAlias(Base):
    __tablename__ = "person_alias"
    __table_args__ = (
        ForeignKeyConstraint(
            ["person_id"], ["person.id"], name="fk_person_alias_person"
        ),
        Index("fk_person_alias_person_idx", "person_id"),
        Index("name_UNIQUE", "name_template", unique=True),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    person_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    name_template: Mapped[str] = mapped_column(String(64), nullable=False)

    person: Mapped[Person] = relationship("Person", back_populates="person_alias")
