from __future__ import annotations

import datetime

from pydantic import Field

from .common import APIModel


class SubjectListItem(APIModel):
    subject_abbrev: str = Field(description="Subject abbreviation (e.g. efo).")
    subject: str = Field(description="Full subject name.")


class PersonLink(APIModel):
    person_id: int
    person_name: str


class ResultsRow(APIModel):
    placement: int | None
    person_name: str | None
    age_group: str | None
    school: str | None
    mentors: list[str]
    fields: list[str]
    person_id: int | None = None
    school_id: int | None = None
    mentor_links: list[PersonLink] = Field(default_factory=list)


class ResultsPayload(APIModel):
    title: str
    contest_name: str
    subcontest: str | None
    age_group: str | None
    contest: str | None
    year: int | None
    start_date: datetime.date | None = None
    end_date: datetime.date | None = None
    subject: str | None
    subject_abbrev: str | None = None
    type: str | None
    columns: list[str]
    rows: list[ResultsRow]
    tasks_link: str | None = None
    solutions_link: str | None = None
    description: str | None = None
