from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from .fakes import FakeResult, FakeSession, ns

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

SessionOverrideSetter = Callable[[FakeSession], None]


def test_list_schools(
    client: TestClient, set_session_override: SessionOverrideSetter
) -> None:
    set_session_override(
        FakeSession(
            results=[FakeResult(rows=[ns(id=1, name="S1"), ns(id=2, name="S2")])]
        )
    )
    resp = client.get("/schools")
    assert resp.status_code == 200
    assert resp.json() == [
        {"school_id": 1, "school_name": "S1"},
        {"school_id": 2, "school_name": "S2"},
    ]


def test_search_schools_rejects_whitespace_query(
    client: TestClient, set_session_override: SessionOverrideSetter
) -> None:
    set_session_override(FakeSession(results=[]))
    resp = client.get("/schools/search", params={"q": "   "})
    assert resp.status_code == 422
    assert resp.json()["detail"] == "Query must not be empty"


def test_search_schools_has_more_headers(
    client: TestClient, set_session_override: SessionOverrideSetter
) -> None:
    set_session_override(
        FakeSession(
            results=[
                FakeResult(scalar_one_or_none_value=3),
                FakeResult(
                    rows=[
                        ns(id=1, name="Alpha"),
                        ns(id=2, name="Alpine"),
                        ns(id=3, name="Alps"),
                    ]
                ),
            ]
        )
    )
    resp = client.get("/schools/search", params={"q": "alp", "offset": 0, "limit": 2})
    assert resp.status_code == 200
    assert resp.headers["X-Result-Has-More"] == "true"
    assert resp.headers["X-Result-Next-Offset"] == "2"
    assert resp.json() == [
        {"school_id": 1, "school_name": "Alpha"},
        {"school_id": 2, "school_name": "Alpine"},
    ]


def test_search_schools_no_more_headers(
    client: TestClient, set_session_override: SessionOverrideSetter
) -> None:
    set_session_override(
        FakeSession(
            results=[
                FakeResult(scalar_one_or_none_value=11),
                FakeResult(rows=[ns(id=7, name="X")]),
            ]
        )
    )
    resp = client.get("/schools/search", params={"q": "x", "offset": 10, "limit": 20})
    assert resp.status_code == 200
    assert resp.headers["X-Result-Has-More"] == "false"
    assert "X-Result-Next-Offset" not in resp.headers


def test_school_students_404_when_school_missing(
    client: TestClient, set_session_override: SessionOverrideSetter
) -> None:
    set_session_override(
        FakeSession(results=[FakeResult(scalar_one_or_none_value=None)])
    )
    resp = client.get("/schools/1/students")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "School not found"


def test_school_students_success(
    client: TestClient, set_session_override: SessionOverrideSetter
) -> None:
    school = ns(id=5, name="Test School")
    set_session_override(
        FakeSession(
            results=[
                FakeResult(scalar_one_or_none_value=school),
                FakeResult(scalar_one_or_none_value=3),
                FakeResult(scalar_one_or_none_value=9),
                FakeResult(
                    rows=[
                        ns(person_id=1, person_name="A", participations=3),
                        ns(person_id=2, person_name="B", participations=0),
                    ]
                ),
            ]
        )
    )
    resp = client.get("/schools/5/students")
    assert resp.status_code == 200
    assert resp.json() == {
        "school_id": 5,
        "school_name": "Test School",
        "total_students": 3,
        "total_participations": 9,
        "students": [
            {"person_id": 1, "person_name": "A", "participations": 3},
            {"person_id": 2, "person_name": "B", "participations": 0},
        ],
        "mentors": None,
    }


def test_school_mentors_success(
    client: TestClient, set_session_override: SessionOverrideSetter
) -> None:
    school = ns(id=7, name="Mentor School")
    set_session_override(
        FakeSession(
            results=[
                FakeResult(scalar_one_or_none_value=school),
                FakeResult(
                    rows=[
                        ns(mentor_id=10, mentor_name="M1", participations=2),
                        ns(mentor_id=11, mentor_name="M2", participations=1),
                    ]
                ),
            ]
        )
    )
    resp = client.get("/schools/7/mentors")
    assert resp.status_code == 200
    assert resp.json() == {
        "school_id": 7,
        "school_name": "Mentor School",
        "total_students": None,
        "total_participations": None,
        "students": None,
        "mentors": [
            {"person_id": 10, "person_name": "M1", "participations": 2},
            {"person_id": 11, "person_name": "M2", "participations": 1},
        ],
    }
