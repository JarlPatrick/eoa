from sqlalchemy import Column, ForeignKeyConstraint, Index, Table
from sqlalchemy.dialects.mysql import INTEGER

from app.db.base import Base

t_mentor = Table(
    "mentor",
    Base.metadata,
    Column("contestant_id", INTEGER(11), primary_key=True),
    Column("mentor_id", INTEGER(11), primary_key=True),
    ForeignKeyConstraint(
        ["contestant_id"],
        ["contestant.id"],
        ondelete="CASCADE",
        name="fk_mentor_contestant",
    ),
    ForeignKeyConstraint(
        ["mentor_id"],
        ["person.id"],
        ondelete="CASCADE",
        name="fk_mentor_mentor",
    ),
    Index("fk_mentor_1_idx", "mentor_id"),
    comment=(
        "Võistleja juhendaja\n\nPeaks olema eraldi tabel, sest võistlejal ei pruugi "
        "juhendajat märgitud olla või võib neid olla mitu"
    ),
)
