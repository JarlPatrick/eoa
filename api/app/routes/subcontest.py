from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_session
from app.domain.subjects import SUBJECT_ABBREV, SUBJECT_BY_ABBREV, SubjectAbbrev
from app.models import AgeGroup, Contest, Subcontest, Subject, Type
from app.schemas import ResultsPayload, SubjectListItem
from app.services.results import ResultsFormat, get_results_payload, payload_as_csv

if TYPE_CHECKING:
    from fastapi.responses import Response

router = APIRouter(tags=["contest"])

SEASON_PATH = Path(
    description=(
        "School-year season in format YYYY-YYYY (end year must be start year + 1)."
    ),
    pattern=r"^\d{4}[-_]\d{4}$",
    examples=["2017-2018"],
)
CONTEST_TYPE_PATH = Path(alias="type")
RESULTS_FORMAT_QUERY = Query(alias="format")


@dataclass(frozen=True, slots=True)
class ResultsLookup:
    subject: SubjectAbbrev
    season: str
    contest_type: str
    age_group: str


def _results_lookup(
    subject: SubjectAbbrev,
    season: Annotated[str, SEASON_PATH],
    contest_type: Annotated[str, CONTEST_TYPE_PATH],
    age_group: str,
) -> ResultsLookup:
    return ResultsLookup(
        subject=subject,
        season=season,
        contest_type=contest_type,
        age_group=age_group,
    )


def _parse_season_start_year(season: str) -> int:
    s = season.strip()
    m = re.match(r"^(?P<y1>\d{4})(?:[-_](?P<y2>\d{4}))?$", s)
    if not m:
        raise HTTPException(status_code=400, detail="Invalid season format")
    y1 = int(m.group("y1"))
    y2 = m.group("y2")
    if y2 is not None and int(y2) != y1 + 1:
        raise HTTPException(
            status_code=400,
            detail="Invalid season (expected end year = start year + 1)",
        )
    return y1


@router.get("/contest", response_model=list[SubjectListItem])
def list_subjects(
    *, session: Annotated[Session, Depends(get_session)]
) -> list[SubjectListItem]:
    subject_names = (
        session.execute(
            select(Subject.name)
            .join(Contest, Contest.subject_id == Subject.id)
            .distinct()
            .order_by(Subject.name)
        )
        .scalars()
        .all()
    )

    missing = [name for name in subject_names if name not in SUBJECT_ABBREV]
    if missing:
        raise HTTPException(
            status_code=500,
            detail=f"Missing hardcoded abbreviations for subjects: {', '.join(sorted(missing))}",
        )

    return [
        SubjectListItem(subject_abbrev=SUBJECT_ABBREV[name], subject=name)
        for name in subject_names
    ]


@router.get("/contest/{subject}", response_model=list[str])
def list_seasons(
    *,
    subject: SubjectAbbrev,
    session: Annotated[Session, Depends(get_session)],
) -> list[str]:
    subject_name = SUBJECT_BY_ABBREV.get(subject.value)
    if subject_name is None:
        raise HTTPException(status_code=400, detail="Invalid subject")

    years = (
        session.execute(
            select(Contest.year)
            .join(Subject, Contest.subject_id == Subject.id)
            .where(Subject.name == subject_name)
            .where(Contest.year.is_not(None))
            .distinct()
            .order_by(Contest.year.desc())
        )
        .scalars()
        .all()
    )
    return [f"{y}-{y + 1}" for y in years if y is not None]


@router.get("/contest/{subject}/{season}", response_model=list[str])
def list_contest_types(
    *,
    subject: SubjectAbbrev,
    season: Annotated[str, SEASON_PATH],
    session: Annotated[Session, Depends(get_session)],
) -> list[str]:
    subject_name = SUBJECT_BY_ABBREV.get(subject.value)
    if subject_name is None:
        raise HTTPException(status_code=400, detail="Invalid subject")

    year = _parse_season_start_year(season)

    types = (
        session.execute(
            select(Type.name)
            .join(Contest, Contest.type_id == Type.id)
            .join(Subject, Contest.subject_id == Subject.id)
            .where(Subject.name == subject_name)
            .where(Contest.year == year)
            .distinct()
            .order_by(Type.name)
        )
        .scalars()
        .all()
    )
    return [t.lower() for t in types if t is not None]


@router.get("/contest/{subject}/{season}/{type}", response_model=list[str])
def list_age_groups(
    *,
    subject: SubjectAbbrev,
    season: Annotated[str, SEASON_PATH],
    contest_type: Annotated[str, CONTEST_TYPE_PATH],
    session: Annotated[Session, Depends(get_session)],
) -> list[str]:
    subject_name = SUBJECT_BY_ABBREV.get(subject.value)
    if subject_name is None:
        raise HTTPException(status_code=400, detail="Invalid subject")

    year = _parse_season_start_year(season)
    contest_type_norm = contest_type.strip().lower()

    age_groups = (
        session.execute(
            select(AgeGroup.name)
            .join(Subcontest, Subcontest.age_group_id == AgeGroup.id)
            .join(Contest, Subcontest.contest_id == Contest.id)
            .join(Subject, Contest.subject_id == Subject.id)
            .join(Type, Contest.type_id == Type.id)
            .where(Subject.name == subject_name)
            .where(Contest.year == year)
            .where(func.lower(Type.name) == contest_type_norm)
            .group_by(AgeGroup.name)
            .order_by(
                func.min(AgeGroup.min_class).is_(None),
                func.min(AgeGroup.min_class),
                AgeGroup.name,
            )
        )
        .scalars()
        .all()
    )
    return [a for a in age_groups if a is not None]


@router.get(
    "/contest/{subject}/{season}/{type}/{age_group}",
    response_model=ResultsPayload,
    responses={200: {"content": {"text/csv": {"schema": {"type": "string"}}}}},
)
def get_results(
    *,
    lookup: Annotated[ResultsLookup, Depends(_results_lookup)],
    session: Annotated[Session, Depends(get_session)],
    results_format: Annotated[ResultsFormat, RESULTS_FORMAT_QUERY] = ResultsFormat.json,
) -> ResultsPayload | Response:
    subject_name = SUBJECT_BY_ABBREV.get(lookup.subject.value)
    if subject_name is None:
        raise HTTPException(status_code=400, detail="Invalid subject")

    year = _parse_season_start_year(lookup.season)
    contest_type_norm = lookup.contest_type.strip().lower()
    age_group_norm = lookup.age_group.strip().lower()

    candidates = (
        session.execute(
            select(Subcontest.id)
            .join(Contest, Subcontest.contest_id == Contest.id)
            .join(Subject, Contest.subject_id == Subject.id)
            .join(Type, Contest.type_id == Type.id)
            .join(AgeGroup, Subcontest.age_group_id == AgeGroup.id)
            .where(Subject.name == subject_name)
            .where(Contest.year == year)
            .where(func.lower(Type.name) == contest_type_norm)
            .where(func.lower(AgeGroup.name) == age_group_norm)
            .order_by(Subcontest.id)
        )
        .scalars()
        .all()
    )

    if not candidates:
        raise HTTPException(status_code=404, detail="No matching subcontest")
    if len(candidates) > 1:
        raise HTTPException(
            status_code=409, detail="Ambiguous: multiple subcontests match"
        )

    subcontest_id = candidates[0]
    payload = get_results_payload(subcontest_id=subcontest_id, session=session)
    payload_model = ResultsPayload.model_validate(payload)
    if results_format == ResultsFormat.json:
        return payload_model
    return payload_as_csv(subcontest_id=subcontest_id, payload=payload_model)


@router.get(
    "/subcontests/{subcontest_id}",
    response_model=ResultsPayload,
    responses={200: {"content": {"text/csv": {"schema": {"type": "string"}}}}},
)
def get_subcontest_by_id(
    *,
    subcontest_id: Annotated[int, Path(gt=0, description="Subcontest ID")],
    session: Annotated[Session, Depends(get_session)],
    results_format: Annotated[ResultsFormat, RESULTS_FORMAT_QUERY] = ResultsFormat.json,
) -> ResultsPayload | Response:
    payload = get_results_payload(subcontest_id=subcontest_id, session=session)
    payload_model = ResultsPayload.model_validate(payload)
    if results_format == ResultsFormat.json:
        return payload_model
    return payload_as_csv(subcontest_id=subcontest_id, payload=payload_model)
