from __future__ import annotations

import csv
import io
from enum import StrEnum
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session

from app.db import get_session
from app.models import AgeGroup, Contestant, Person, Subcontest, t_mentor
from app.schemas import StudentStatisticsResponse
from app.security import require_internal_api

router = APIRouter(tags=["statistics"], dependencies=[Depends(require_internal_api)])


class StatisticsFormat(StrEnum):
    json = "json"
    csv = "csv"


FIRST_PLACE = 1
SECOND_PLACE = 2
THIRD_PLACE = 3
MIN_PARTICIPATIONS = 10


def _weight_expr() -> object:
    grades = AgeGroup.max_class - AgeGroup.min_class + 1
    return func.least(3, func.greatest(1, func.coalesce(grades, 1)))


@router.get(
    "/statistics/students",
    response_model=StudentStatisticsResponse,
    responses={200: {"content": {"text/csv": {"schema": {"type": "string"}}}}},
)
def student_statistics(
    *,
    session: Annotated[Session, Depends(get_session)],
    weighted: Annotated[
        bool,
        Query(
            description=(
                "If true, 1st/2nd/3rd place sums are weighted by "
                "min(3, max(1, age_group.max_class - age_group.min_class + 1))."
            )
        ),
    ] = False,
    statistics_format: Annotated[
        StatisticsFormat,
        Query(alias="format"),
    ] = StatisticsFormat.json,
) -> StudentStatisticsResponse | Response:
    place_value = _weight_expr() if weighted else 1

    total_participations = func.count().label("total_participations")
    first_places = func.sum(
        case((Contestant.placement == FIRST_PLACE, place_value), else_=0)
    ).label("first_places")
    second_places = func.sum(
        case((Contestant.placement == SECOND_PLACE, place_value), else_=0)
    ).label("second_places")
    third_places = func.sum(
        case((Contestant.placement == THIRD_PLACE, place_value), else_=0)
    ).label("third_places")

    rows = session.execute(
        select(
            Person.id.label("person_id"),
            Person.name.label("person_name"),
            total_participations,
            first_places,
            second_places,
            third_places,
        )
        .select_from(Contestant)
        .join(Person, Contestant.person_id == Person.id)
        .join(Subcontest, Contestant.subcontest_id == Subcontest.id)
        .join(AgeGroup, Subcontest.age_group_id == AgeGroup.id)
        .group_by(Person.id, Person.name)
        .having(
            or_(
                total_participations >= MIN_PARTICIPATIONS,
                (first_places + second_places + third_places) > 0,
            )
        )
        .order_by(
            total_participations.desc(),
            first_places.desc(),
            second_places.desc(),
            third_places.desc(),
            Person.name,
        )
    ).all()

    fields = [
        "person_id",
        "person_name",
        "total_participations",
        "first_places",
        "second_places",
        "third_places",
    ]
    payload_rows = [
        [
            r.person_id,
            r.person_name,
            int(r.total_participations),
            int(r.first_places or 0),
            int(r.second_places or 0),
            int(r.third_places or 0),
        ]
        for r in rows
    ]

    if statistics_format == StatisticsFormat.json:
        return StudentStatisticsResponse(fields=fields, rows=payload_rows)

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(fields)
    writer.writerows(payload_rows)

    suffix = "_weighted" if weighted else ""
    return Response(
        content=buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="student_statistics{suffix}.csv"'
        },
    )


@router.get("/statistics/mentors", response_model=StudentStatisticsResponse)
def mentor_statistics(
    session: Annotated[Session, Depends(get_session)],
    *,
    weighted: bool = True,
    statistics_format: Annotated[
        StatisticsFormat, Query(alias="format")
    ] = StatisticsFormat.json,
) -> StudentStatisticsResponse | Response:
    place_value = _weight_expr() if weighted else 1
    total = func.count(Contestant.id).label("total_participations")
    first = func.sum(
        case((Contestant.placement == FIRST_PLACE, place_value), else_=0)
    ).label("first_places")
    second = func.sum(
        case((Contestant.placement == SECOND_PLACE, place_value), else_=0)
    ).label("second_places")
    third = func.sum(
        case((Contestant.placement == THIRD_PLACE, place_value), else_=0)
    ).label("third_places")
    student = Person.__table__.alias("student")
    rows = session.execute(
        select(Person.id, Person.name, total, first, second, third)
        .select_from(t_mentor)
        .join(Person, t_mentor.c.mentor_id == Person.id)
        .join(Contestant, t_mentor.c.contestant_id == Contestant.id)
        .join(student, Contestant.person_id == student.c.id)
        .join(Subcontest, Contestant.subcontest_id == Subcontest.id)
        .join(AgeGroup, Subcontest.age_group_id == AgeGroup.id)
        .group_by(Person.id, Person.name)
        .having(or_(total >= MIN_PARTICIPATIONS, first + second + third > 0))
        .order_by(total.desc(), first.desc(), second.desc(), third.desc(), Person.name)
    ).all()
    fields = [
        "person_id",
        "person_name",
        "total_participations",
        "first_places",
        "second_places",
        "third_places",
    ]
    payload = [
        [
            r.id,
            r.name,
            int(r.total_participations),
            int(r.first_places or 0),
            int(r.second_places or 0),
            int(r.third_places or 0),
        ]
        for r in rows
    ]
    if statistics_format == StatisticsFormat.json:
        return StudentStatisticsResponse(fields=fields, rows=payload)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(fields)
    writer.writerows(payload)
    return Response(
        content=buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="mentor_statistics.csv"'},
    )
