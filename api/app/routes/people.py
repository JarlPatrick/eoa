from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_session
from app.domain.subjects import SUBJECT_ABBREV
from app.models import (
    AgeGroup,
    Contest,
    Contestant,
    Person,
    School,
    Subcontest,
    Subject,
    Type,
    t_mentor,
)
from app.schemas import ContestantEntry, MentorEntry, PersonSummary

router = APIRouter(tags=["people"])


@router.get("/people/search", response_model=list[PersonSummary])
def search_people(
    *,
    q: Annotated[
        str,
        Query(min_length=1, description="Substring search in person name."),
    ],
    response: Response,
    session: Annotated[Session, Depends(get_session)],
    offset: Annotated[int, Query(ge=0, description="Pagination offset.")] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 20,
    role: Literal["student", "mentor"] = "student",
) -> list[PersonSummary]:
    query = q.strip()
    if not query:
        raise HTTPException(status_code=422, detail="Query must not be empty")

    eligible = (
        Person.id.in_(select(Contestant.person_id))
        if role == "student"
        else Person.id.in_(select(t_mentor.c.mentor_id))
    )
    predicate = (
        Person.name.contains(query, autoescape=True),
        eligible,
    )
    total = session.scalar(select(func.count(Person.id)).where(*predicate)) or 0
    rows = session.execute(
        select(Person.id, Person.name)
        .where(*predicate)
        .order_by(Person.name, Person.id)
        .offset(offset)
        .limit(limit + 1)
    ).all()

    has_more = len(rows) > limit
    response.headers["X-Result-Limit"] = str(limit)
    response.headers["X-Result-Offset"] = str(offset)
    response.headers["X-Result-Has-More"] = "true" if has_more else "false"
    response.headers["X-Result-Count"] = str(min(len(rows), limit))
    response.headers["X-Result-Total"] = str(total)
    if has_more:
        response.headers["X-Result-Next-Offset"] = str(offset + limit)

    return [PersonSummary(person_id=r.id, person_name=r.name) for r in rows[:limit]]


@router.get("/people/{person_id}", response_model=PersonSummary)
def get_person(
    *,
    person_id: Annotated[int, Path(gt=0)],
    session: Annotated[Session, Depends(get_session)],
) -> PersonSummary:
    row = session.execute(
        select(Person.id, Person.name).where(Person.id == person_id)
    ).one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Not found")
    return PersonSummary(person_id=row.id, person_name=row.name)


def _season(year: int | None) -> str | None:
    if year is None:
        return None
    return f"{year}-{year + 1}"


def _subject_abbrev(subject_name: str | None) -> str | None:
    if subject_name is None:
        return None
    return SUBJECT_ABBREV.get(subject_name)


@router.get("/contestant/{person_id}", response_model=list[ContestantEntry])
def contestant(
    *,
    person_id: Annotated[int, Path(gt=0, description="Person ID.")],
    session: Annotated[Session, Depends(get_session)],
) -> list[ContestantEntry]:
    person_row = session.execute(
        select(Person.name).where(Person.id == person_id)
    ).one_or_none()
    if person_row is None:
        raise HTTPException(status_code=404, detail="Not found")
    person_name: str = person_row.name

    rows = session.execute(
        select(
            Contestant.id.label("contestant_id"),
            Subject.name.label("subject_name"),
            Type.name.label("type_name"),
            Contest.year.label("year"),
            AgeGroup.name.label("age_group"),
            Contestant.placement.label("placement"),
            Contestant.subcontest_id.label("subcontest_id"),
            School.id.label("school_id"),
            School.name.label("school_name"),
        )
        .select_from(Contestant)
        .join(Person, Contestant.person_id == Person.id)
        .join(Subcontest, Contestant.subcontest_id == Subcontest.id)
        .join(Contest, Subcontest.contest_id == Contest.id)
        .join(Subject, Contest.subject_id == Subject.id, isouter=True)
        .join(Type, Contest.type_id == Type.id, isouter=True)
        .join(AgeGroup, Contestant.age_group_id == AgeGroup.id, isouter=True)
        .join(School, Contestant.school_id == School.id, isouter=True)
        .where(Contestant.person_id == person_id)
        .order_by(Contest.year.is_(None), Contest.year.desc(), Type.name, AgeGroup.name)
    ).all()

    mentors_by_contestant: dict[int, list[PersonSummary]] = {}
    if rows:
        mentor_rows = session.execute(
            select(t_mentor.c.contestant_id, Person.id, Person.name)
            .join(Person, t_mentor.c.mentor_id == Person.id)
            .where(t_mentor.c.contestant_id.in_([r.contestant_id for r in rows]))
            .order_by(Person.name)
        ).all()
        for mentor_row in mentor_rows:
            mentors_by_contestant.setdefault(mentor_row.contestant_id, []).append(
                PersonSummary(person_id=mentor_row.id, person_name=mentor_row.name)
            )

    out: list[ContestantEntry] = []
    missing: set[str] = set()
    for r in rows:
        subj_abbrev = _subject_abbrev(r.subject_name)
        if r.subject_name is not None and subj_abbrev is None:
            missing.add(r.subject_name)
        out.append(
            ContestantEntry(
                person_name=person_name,
                subject=subj_abbrev,
                type=(r.type_name or "").lower() if r.type_name else None,
                season=_season(r.year),
                age_group=r.age_group,
                placement=r.placement,
                subcontest_id=r.subcontest_id,
                subject_name=r.subject_name,
                school_id=r.school_id,
                school_name=r.school_name,
                mentors=mentors_by_contestant.get(r.contestant_id, []),
            )
        )

    if missing:
        raise HTTPException(
            status_code=500,
            detail=f"Missing hardcoded abbreviations for subjects: {', '.join(sorted(missing))}",
        )

    return out


@router.get("/mentor/{person_id}", response_model=list[MentorEntry])
def mentor(
    *,
    person_id: Annotated[
        int,
        Path(gt=0, description="Mentor person ID."),
    ],
    session: Annotated[Session, Depends(get_session)],
) -> list[MentorEntry]:
    mentor_row = session.execute(
        select(Person.name).where(Person.id == person_id)
    ).one_or_none()
    if mentor_row is None:
        raise HTTPException(status_code=404, detail="Not found")
    mentor_name: str = mentor_row.name

    student = Person.__table__.alias("student")

    rows = session.execute(
        select(
            student.c.id.label("student_id"),
            student.c.name.label("student_name"),
            Subject.name.label("subject_name"),
            Type.name.label("type_name"),
            Contest.year.label("year"),
            AgeGroup.name.label("age_group"),
            Contestant.placement.label("placement"),
            Contestant.subcontest_id.label("subcontest_id"),
            School.id.label("school_id"),
            School.name.label("school_name"),
        )
        .select_from(t_mentor)
        .join(Contestant, t_mentor.c.contestant_id == Contestant.id)
        .join(student, Contestant.person_id == student.c.id)
        .join(Subcontest, Contestant.subcontest_id == Subcontest.id)
        .join(Contest, Subcontest.contest_id == Contest.id)
        .join(Subject, Contest.subject_id == Subject.id, isouter=True)
        .join(Type, Contest.type_id == Type.id, isouter=True)
        .join(AgeGroup, Contestant.age_group_id == AgeGroup.id, isouter=True)
        .join(School, Contestant.school_id == School.id, isouter=True)
        .where(t_mentor.c.mentor_id == person_id)
        .order_by(Contest.year.is_(None), Contest.year.desc(), Type.name, AgeGroup.name)
    ).all()

    out: list[MentorEntry] = []
    missing: set[str] = set()
    for r in rows:
        subj_abbrev = _subject_abbrev(r.subject_name)
        if r.subject_name is not None and subj_abbrev is None:
            missing.add(r.subject_name)
        out.append(
            MentorEntry(
                mentor_name=mentor_name,
                student_name=r.student_name,
                subject=subj_abbrev,
                type=(r.type_name or "").lower() if r.type_name else None,
                season=_season(r.year),
                age_group=r.age_group,
                placement=r.placement,
                subcontest_id=r.subcontest_id,
                subject_name=r.subject_name,
                student_id=r.student_id,
                school_id=r.school_id,
                school_name=r.school_name,
            )
        )

    if missing:
        raise HTTPException(
            status_code=500,
            detail=f"Missing hardcoded abbreviations for subjects: {', '.join(sorted(missing))}",
        )

    return out
