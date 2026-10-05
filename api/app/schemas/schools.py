from __future__ import annotations

from pydantic import Field

from .common import APIModel


class SchoolSummary(APIModel):
    school_id: int = Field(ge=1)
    school_name: str


class SchoolParticipation(APIModel):
    person_id: int = Field(ge=1)
    person_name: str
    participations: int = Field(ge=0)


class SchoolParticipantsResponse(APIModel):
    school_id: int = Field(ge=1)
    school_name: str
    total_students: int | None = Field(default=None, ge=0)
    total_participations: int | None = Field(default=None, ge=0)
    students: list[SchoolParticipation] | None = None
    mentors: list[SchoolParticipation] | None = None
