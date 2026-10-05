"""Read-only data tailored to the public website."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import String, case, cast, func, or_, select
from sqlalchemy.orm import Session

from app.db import get_session
from app.domain.subjects import SUBJECT_ABBREV, SUBJECT_BY_ABBREV
from app.models import (
    AgeGroup,
    Contest,
    Contestant,
    Person,
    School,
    Subcontest,
    Subject,
    Type,
)
from app.security import require_internal_api

router = APIRouter(
    prefix="/site", tags=["site"], dependencies=[Depends(require_internal_api)]
)
FIRST_PLACE = 1
SECOND_PLACE = 2
THIRD_PLACE = 3


@router.get("/contests")
def site_contests(
    session: Annotated[Session, Depends(get_session)],
    response: Response,
    subject: str | None = None,
    q: str | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[dict[str, object]]:
    filters = []
    if subject is not None:
        name = SUBJECT_BY_ABBREV.get(subject)
        if name is None:
            raise HTTPException(status_code=404, detail="Subject not found")
        filters.append(Subject.name == name)
    if q:
        filters.extend(
            or_(
                Subject.name.contains(term, autoescape=True),
                Type.name.contains(term, autoescape=True),
                Contest.name.contains(term, autoescape=True),
                Subcontest.name.contains(term, autoescape=True),
                AgeGroup.name.contains(term, autoescape=True),
                cast(Contest.year, String).contains(term, autoescape=True),
                func.concat(Contest.year, "/", Contest.year + 1).contains(
                    term, autoescape=True
                ),
            )
            for term in q.strip().split()
        )
    query = (
        select(
            Subcontest.id,
            Subcontest.name.label("subcontest_name"),
            Subcontest.tasks_link,
            Subcontest.solutions_link,
            Contest.name.label("contest_name"),
            Contest.year,
            Subject.name.label("subject"),
            Type.name.label("contest_type"),
            AgeGroup.name.label("age_group"),
            select(func.count(Contestant.id))
            .where(Contestant.subcontest_id == Subcontest.id)
            .correlate(Subcontest)
            .scalar_subquery()
            .label("result_count"),
        )
        .join(Contest, Subcontest.contest_id == Contest.id)
        .join(Subject, Contest.subject_id == Subject.id)
        .join(Type, Contest.type_id == Type.id)
        .join(AgeGroup, Subcontest.age_group_id == AgeGroup.id)
        .where(*filters)
        .order_by(
            Subject.name,
            Contest.year.desc(),
            Type.name,
            AgeGroup.min_class,
            Subcontest.id,
        )
    )
    if q:
        count_query = (
            select(func.count(Subcontest.id))
            .join(Contest, Subcontest.contest_id == Contest.id)
            .join(Subject, Contest.subject_id == Subject.id)
            .join(Type, Contest.type_id == Type.id)
            .join(AgeGroup, Subcontest.age_group_id == AgeGroup.id)
            .where(*filters)
        )
        response.headers["X-Result-Total"] = str(session.scalar(count_query) or 0)
        query = query.offset(offset).limit(limit)
    rows = session.execute(query).all()
    return [
        {
            "id": row.id,
            "subcontest_name": row.subcontest_name,
            "tasks_link": row.tasks_link,
            "solutions_link": row.solutions_link,
            "result_count": row.result_count,
            "contest_name": row.contest_name,
            "year": row.year,
            "subject": row.subject,
            "subject_abbrev": SUBJECT_ABBREV[row.subject],
            "contest_type": row.contest_type,
            "age_group": row.age_group,
        }
        for row in rows
    ]


@router.get("/home")
def site_home(session: Annotated[Session, Depends(get_session)]) -> dict[str, object]:
    subject_count = session.scalar(select(func.count(Subject.id))) or 0
    contest_count = session.scalar(select(func.count(Contest.id))) or 0
    season_count = session.scalar(select(func.count(func.distinct(Contest.year)))) or 0
    person_count = session.scalar(select(func.count(Person.id))) or 0
    school_count = session.scalar(select(func.count(School.id))) or 0
    latest_year = session.scalar(
        select(func.max(Contest.year)).join(
            Subcontest, Subcontest.contest_id == Contest.id
        )
    )
    recent = []
    if latest_year is not None:
        rows = session.execute(
            select(
                Subcontest.id,
                Subcontest.name.label("subcontest_name"),
                Contest.name.label("contest_name"),
                Contest.start_date,
                Contest.end_date,
                Subject.name.label("subject"),
                Type.name.label("contest_type"),
                AgeGroup.name.label("age_group"),
            )
            .join(Contest, Subcontest.contest_id == Contest.id)
            .join(Subject, Contest.subject_id == Subject.id)
            .join(Type, Contest.type_id == Type.id)
            .join(AgeGroup, Subcontest.age_group_id == AgeGroup.id)
            .where(Contest.year == latest_year)
            .order_by(
                func.coalesce(Contest.start_date, Contest.end_date).desc(),
                Contest.end_date.desc(),
                Subject.name,
                Type.name,
                AgeGroup.min_class,
                Subcontest.id,
            )
        ).all()
        recent = [
            {
                "id": row.id,
                "subcontest_name": row.subcontest_name,
                "contest_name": row.contest_name,
                "start_date": row.start_date,
                "end_date": row.end_date,
                "subject": row.subject,
                "subject_abbrev": SUBJECT_ABBREV[row.subject],
                "contest_type": row.contest_type,
                "age_group": row.age_group,
            }
            for row in rows
        ]
    # The schema has no insertion timestamp; the auto-incremented subcontest ID
    # is the available ordering for newly inserted result records.
    added_rows = session.execute(
        select(
            Subcontest.id,
            Subcontest.name.label("subcontest_name"),
            Contest.name.label("contest_name"),
            Contest.year,
            Subject.name.label("subject"),
            Type.name.label("contest_type"),
            AgeGroup.name.label("age_group"),
        )
        .join(Contest, Subcontest.contest_id == Contest.id)
        .join(Subject, Contest.subject_id == Subject.id)
        .join(Type, Contest.type_id == Type.id)
        .join(AgeGroup, Subcontest.age_group_id == AgeGroup.id)
        .order_by(Subcontest.id.desc())
        .limit(16)
    ).all()
    recent_added = [
        {
            "id": row.id,
            "subcontest_name": row.subcontest_name,
            "contest_name": row.contest_name,
            "year": row.year,
            "subject": row.subject,
            "subject_abbrev": SUBJECT_ABBREV[row.subject],
            "contest_type": row.contest_type,
            "age_group": row.age_group,
        }
        for row in added_rows
    ]
    return {
        "subjects": subject_count,
        "contests": contest_count,
        "seasons": season_count,
        "people": person_count,
        "schools": school_count,
        "latest_year": latest_year,
        "recent": recent,
        "recent_added": recent_added,
    }


@router.get("/schools")
def site_school_rankings(
    session: Annotated[Session, Depends(get_session)],
) -> list[dict[str, object]]:
    total_students = func.count(func.distinct(Person.id))
    rows = session.execute(
        select(
            School.id,
            School.name,
            func.count(Contestant.id).label("participations"),
            total_students.label("students"),
            func.sum(
                case(
                    (
                        Contestant.placement == FIRST_PLACE,
                        1,
                    ),
                    else_=0,
                )
            ).label("first_places"),
            func.sum(
                case(
                    (
                        Contestant.placement == SECOND_PLACE,
                        1,
                    ),
                    else_=0,
                )
            ).label("second_places"),
            func.sum(
                case(
                    (
                        Contestant.placement == THIRD_PLACE,
                        1,
                    ),
                    else_=0,
                )
            ).label("third_places"),
        )
        .select_from(School)
        .join(Contestant, Contestant.school_id == School.id)
        .join(Person, Contestant.person_id == Person.id)
        .group_by(School.id, School.name)
        .order_by(func.count(Contestant.id).desc(), School.name)
    ).all()
    return [
        {
            "school_id": row.id,
            "school_name": row.name,
            "participations": int(row.participations),
            "students": int(row.students),
            "first_places": int(row.first_places or 0),
            "second_places": int(row.second_places or 0),
            "third_places": int(row.third_places or 0),
        }
        for row in rows
    ]
