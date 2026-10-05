from __future__ import annotations

import csv
import io
from enum import StrEnum
from typing import TYPE_CHECKING

from fastapi import HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.domain.subjects import SUBJECT_ABBREV
from app.models import (
    Contest,
    Contestant,
    ContestantField,
    Subcontest,
    SubcontestColumn,
)

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from app.schemas import ResultsPayload


class ResultsFormat(StrEnum):
    json = "json"
    csv = "csv"


def contest_display_name(subcontest: Subcontest) -> str:
    contest = subcontest.contest
    contest_name = contest.name or ""
    year = contest.year
    if year is not None and str(year) not in contest_name:
        contest_name = f"{contest_name} ({year}/{year + 1})".strip()
    return contest_name


def get_results_payload(*, subcontest_id: int, session: Session) -> dict[str, object]:
    subcontest = session.execute(
        select(Subcontest)
        .where(Subcontest.id == subcontest_id)
        .options(
            joinedload(Subcontest.contest).joinedload(Contest.subject),
            joinedload(Subcontest.contest).joinedload(Contest.type),
            joinedload(Subcontest.age_group),
        )
    ).scalar_one_or_none()

    if subcontest is None:
        raise HTTPException(status_code=404, detail="Subcontest not found")

    columns = (
        session.execute(
            select(SubcontestColumn)
            .where(SubcontestColumn.subcontest_id == subcontest_id)
            .order_by(SubcontestColumn.seq_no, SubcontestColumn.id)
        )
        .scalars()
        .all()
    )
    task_ids = [c.id for c in columns]

    contestants = (
        session.execute(
            select(Contestant)
            .where(Contestant.subcontest_id == subcontest_id)
            .options(
                joinedload(Contestant.person),
                joinedload(Contestant.age_group),
                joinedload(Contestant.school),
                joinedload(Contestant.mentor),
            )
            .order_by(
                Contestant.placement.is_(None), Contestant.placement, Contestant.id
            )
        )
        .unique()
        .scalars()
        .all()
    )

    entries_by_task_and_contestant: dict[int, dict[int, str]] = {
        tid: {} for tid in task_ids
    }
    if task_ids:
        rows = session.execute(
            select(
                ContestantField.task_id,
                ContestantField.contestant_id,
                ContestantField.entry,
            ).where(ContestantField.task_id.in_(task_ids))
        ).all()
        for task_id, contestant_id, entry in rows:
            entries_by_task_and_contestant.setdefault(task_id, {})[contestant_id] = (
                entry
            )

    contest_name = contest_display_name(subcontest)
    title = ""
    contest = subcontest.contest
    if (
        contest.subject is not None
        and contest.type is not None
        and contest.year is not None
    ):
        title = (
            f"{contest.subject.name} {contest.type.name.lower()} "
            f"{contest.year}/{contest.year + 1} - {subcontest.age_group.name}"
        )

    def maybe_name(value: object) -> str | None:
        if value is None:
            return None
        name = getattr(value, "name", None)
        return name if isinstance(name, str) else None

    def public_row(c: Contestant) -> dict[str, object]:
        mentors = sorted(c.mentor, key=lambda p: p.name)
        return {
            "placement": c.placement,
            "person_id": c.person_id,
            "person_name": maybe_name(c.person),
            "age_group": maybe_name(c.age_group),
            "school_id": c.school_id,
            "school": maybe_name(c.school),
            "mentors": [m.name for m in mentors],
            "mentor_links": [
                {"person_id": m.id, "person_name": m.name} for m in mentors
            ],
            "fields": [
                entries_by_task_and_contestant.get(col.id, {}).get(c.id, "")
                for col in columns
            ],
        }

    subject_name = maybe_name(contest.subject)
    return {
        "title": title,
        "contest_name": contest_name,
        "subcontest": subcontest.name,
        "age_group": subcontest.age_group.name,
        "contest": contest.name,
        "year": contest.year,
        "start_date": contest.start_date,
        "end_date": contest.end_date,
        "subject": subject_name,
        "subject_abbrev": SUBJECT_ABBREV.get(subject_name) if subject_name else None,
        "type": maybe_name(contest.type),
        "columns": [c.name for c in columns],
        "tasks_link": subcontest.tasks_link,
        "solutions_link": subcontest.solutions_link,
        "description": subcontest.description,
        "rows": [public_row(c) for c in contestants],
    }


def payload_as_csv(*, subcontest_id: int, payload: ResultsPayload) -> Response:
    columns = payload.columns
    rows = payload.rows

    has_age_group = any((r.age_group or "") != "" for r in rows)
    has_school = any((r.school or "") != "" for r in rows)
    has_mentor = any(len(r.mentors) > 0 for r in rows)

    headers: list[str] = ["Koht", "Nimi"]
    if has_age_group:
        headers.append("Klass")
    if has_school:
        headers.append("Kool")
    if has_mentor:
        headers.append("Juhendaja")
    headers.extend(columns)

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)

    for row in rows:
        out_row: list[str] = [
            "" if row.placement is None else str(row.placement),
            str(row.person_name or ""),
        ]
        if has_age_group:
            out_row.append(str(row.age_group or ""))
        if has_school:
            out_row.append(str(row.school or ""))
        if has_mentor:
            out_row.append(" / ".join(m for m in row.mentors if m))

        fields = row.fields
        out_row.extend(str(v or "") for v in fields[: len(columns)])
        out_row.extend("" for _ in range(len(columns) - len(fields)))

        writer.writerow(out_row)

    return Response(
        content=buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": (
                f'attachment; filename="subcontest_{subcontest_id}_results.csv"'
            )
        },
    )
