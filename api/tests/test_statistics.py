from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from .fakes import FakeResult, FakeSession, ns

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

SessionOverrideSetter = Callable[[FakeSession], None]


def test_student_statistics_json_default(
    client: TestClient, set_session_override: SessionOverrideSetter
) -> None:
    set_session_override(
        FakeSession(
            results=[
                FakeResult(
                    rows=[
                        ns(
                            person_id=1,
                            person_name="Alice",
                            total_participations=10,
                            first_places=2,
                            second_places=None,
                            third_places=1,
                        )
                    ]
                )
            ]
        )
    )
    resp = client.get("/statistics/students")
    assert resp.status_code == 200
    assert resp.json() == {
        "fields": [
            "person_id",
            "person_name",
            "total_participations",
            "first_places",
            "second_places",
            "third_places",
        ],
        "rows": [[1, "Alice", 10, 2, 0, 1]],
    }


def test_student_statistics_csv_format(
    client: TestClient, set_session_override: SessionOverrideSetter
) -> None:
    set_session_override(
        FakeSession(
            results=[
                FakeResult(
                    rows=[
                        ns(
                            person_id=1,
                            person_name="Alice",
                            total_participations=12,
                            first_places=1,
                            second_places=0,
                            third_places=0,
                        )
                    ]
                )
            ]
        )
    )
    resp = client.get("/statistics/students", params={"format": "csv"})
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    assert (
        'attachment; filename="student_statistics.csv"'
        in resp.headers["content-disposition"]
    )
    assert resp.text.splitlines()[0].split(",") == [
        "person_id",
        "person_name",
        "total_participations",
        "first_places",
        "second_places",
        "third_places",
    ]


def test_student_statistics_csv_weighted_has_filename_suffix(
    client: TestClient, set_session_override: SessionOverrideSetter
) -> None:
    set_session_override(FakeSession(results=[FakeResult(rows=[])]))
    resp = client.get(
        "/statistics/students", params={"format": "csv", "weighted": True}
    )
    assert resp.status_code == 200
    assert "student_statistics_weighted.csv" in resp.headers["content-disposition"]
