from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from .fakes import FakeResult, FakeSession, ns

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

SessionOverrideSetter = Callable[[FakeSession], None]


def test_site_contests(
    client: TestClient, set_session_override: SessionOverrideSetter
) -> None:
    set_session_override(
        FakeSession(
            results=[
                FakeResult(
                    rows=[
                        ns(
                            id=17,
                            subcontest_name="12. klass",
                            tasks_link=None,
                            solutions_link=None,
                            result_count=2,
                            contest_name="Füüsika lõppvoor",
                            year=2025,
                            subject="Füüsika",
                            contest_type="Lõppvoor",
                            age_group="12. klass",
                        )
                    ]
                )
            ]
        )
    )
    response = client.get("/site/contests")
    assert response.status_code == 200
    assert response.json()[0]["id"] == 17
    assert response.json()[0]["subject"] == "Füüsika"


def test_site_home(
    client: TestClient, set_session_override: SessionOverrideSetter
) -> None:
    set_session_override(
        FakeSession(
            results=[
                FakeResult(scalar_one_or_none_value=5),
                FakeResult(scalar_one_or_none_value=20),
                FakeResult(scalar_one_or_none_value=3),
                FakeResult(scalar_one_or_none_value=200),
                FakeResult(scalar_one_or_none_value=12),
                FakeResult(scalar_one_or_none_value=2025),
                FakeResult(
                    rows=[
                        ns(
                            id=1,
                            subcontest_name="Vanem",
                            contest_name="Võistlus",
                            start_date=None,
                            end_date=None,
                            subject="Füüsika",
                            contest_type="Lõppvoor",
                            age_group="Vanem",
                        )
                    ]
                ),
                FakeResult(rows=[]),
            ]
        )
    )
    response = client.get("/site/home")
    assert response.status_code == 200
    assert response.json()["people"] == 200
    assert response.json()["recent"][0]["id"] == 1


def test_site_schools(
    client: TestClient, set_session_override: SessionOverrideSetter
) -> None:
    set_session_override(
        FakeSession(
            results=[
                FakeResult(
                    rows=[
                        ns(
                            id=4,
                            name="Kool",
                            participations=5,
                            students=2,
                            first_places=1,
                            second_places=0,
                            third_places=0,
                        )
                    ]
                )
            ]
        )
    )
    response = client.get("/site/schools")
    assert response.status_code == 200
    assert response.json() == [
        {
            "school_id": 4,
            "school_name": "Kool",
            "participations": 5,
            "students": 2,
            "first_places": 1,
            "second_places": 0,
            "third_places": 0,
        }
    ]


def test_person_is_not_found(
    client: TestClient, set_session_override: SessionOverrideSetter
) -> None:
    set_session_override(FakeSession(results=[FakeResult(one_or_none_row=None)]))
    response = client.get("/people/4")
    assert response.status_code == 404
