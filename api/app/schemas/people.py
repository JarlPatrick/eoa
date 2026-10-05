from __future__ import annotations

from pydantic import Field

from .common import APIModel


class PersonSummary(APIModel):
    person_id: int = Field(ge=1)
    person_name: str


class ContestantEntry(APIModel):
    person_name: str
    subject: str | None
    type: str | None
    season: str | None
    age_group: str | None
    placement: int | None
    subcontest_id: int
    subject_name: str | None = None
    school_id: int | None = None
    school_name: str | None = None
    mentors: list[PersonSummary] = Field(default_factory=list)


class MentorEntry(APIModel):
    mentor_name: str
    student_name: str
    subject: str | None
    type: str | None
    season: str | None
    age_group: str | None
    placement: int | None
    subcontest_id: int
    subject_name: str | None = None
    student_id: int | None = None
    school_id: int | None = None
    school_name: str | None = None
