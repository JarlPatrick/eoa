from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from fastapi import HTTPException

import app.routes.subcontest as subcontest_routes

from .fakes import FakeResult, FakeSession

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch
    from fastapi.testclient import TestClient

SessionOverrideSetter = Callable[[FakeSession], None]


def _payload_dict(*, title: str = "T", subcontest_id: int = 123) -> dict[str, object]:
    return {
        "title": f"{title}-{subcontest_id}",
        "contest_name": "Contest Name",
        "subcontest": "Subcontest",
        "age_group": "12. klass",
        "contest": "Contest",
        "year": 2023,
        "subject": "Füüsika",
        "type": "Lahtine",
        "columns": ["Task 1"],
        "rows": [
            {
                "placement": 1,
                "person_name": "Alice",
                "age_group": "12. klass",
                "school": "School",
                "mentors": ["Mentor"],
                "fields": ["10"],
            }
        ],
    }


def fake_get_results_payload(
    *, subcontest_id: int, session: object
) -> dict[str, object]:
    _ = session
    return _payload_dict(subcontest_id=subcontest_id)


def test_list_subjects_success(
    client: TestClient, set_session_override: SessionOverrideSetter
) -> None:
    set_session_override(
        FakeSession(results=[FakeResult(scalars_list=["Füüsika", "Matemaatika"])])
    )
    resp = client.get("/contest")
    assert resp.status_code == 200
    assert resp.json() == [
        {"subject_abbrev": "efo", "subject": "Füüsika"},
        {"subject_abbrev": "emo", "subject": "Matemaatika"},
    ]


def test_list_subjects_missing_abbrev_is_500(
    client: TestClient, set_session_override: SessionOverrideSetter
) -> None:
    set_session_override(FakeSession(results=[FakeResult(scalars_list=["Not In Map"])]))
    resp = client.get("/contest")
    assert resp.status_code == 500
    assert "Missing hardcoded abbreviations for subjects:" in resp.json()["detail"]


def test_list_seasons_filters_none(
    client: TestClient, set_session_override: SessionOverrideSetter
) -> None:
    set_session_override(
        FakeSession(results=[FakeResult(scalars_list=[2023, None, 2021])])
    )
    resp = client.get("/contest/efo")
    assert resp.status_code == 200
    assert resp.json() == ["2023-2024", "2021-2022"]


def test_list_contest_types_invalid_season_end_year_is_400(
    client: TestClient,
    set_session_override: SessionOverrideSetter,
) -> None:
    set_session_override(FakeSession(results=[]))
    resp = client.get("/contest/efo/2023-2025")
    assert resp.status_code == 400
    assert "Invalid season" in resp.json()["detail"]


def test_list_contest_types_lowercases_and_filters_none(
    client: TestClient, set_session_override: SessionOverrideSetter
) -> None:
    set_session_override(
        FakeSession(results=[FakeResult(scalars_list=["Lahtine", None, "Lõppvoor"])])
    )
    resp = client.get("/contest/efo/2023-2024")
    assert resp.status_code == 200
    assert resp.json() == ["lahtine", "lõppvoor"]


def test_list_age_groups_filters_none(
    client: TestClient, set_session_override: SessionOverrideSetter
) -> None:
    set_session_override(
        FakeSession(results=[FakeResult(scalars_list=["10. klass", None, "11. klass"])])
    )
    resp = client.get("/contest/efo/2023-2024/lahtine")
    assert resp.status_code == 200
    assert resp.json() == ["10. klass", "11. klass"]


def test_get_results_404_when_no_matching_subcontest(
    client: TestClient, set_session_override: SessionOverrideSetter
) -> None:
    set_session_override(FakeSession(results=[FakeResult(scalars_list=[])]))
    resp = client.get("/contest/efo/2023-2024/lahtine/12.%20klass")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "No matching subcontest"


def test_get_results_409_when_ambiguous(
    client: TestClient, set_session_override: SessionOverrideSetter
) -> None:
    set_session_override(FakeSession(results=[FakeResult(scalars_list=[1, 2])]))
    resp = client.get("/contest/efo/2023-2024/lahtine/12.%20klass")
    assert resp.status_code == 409
    assert resp.json()["detail"].startswith("Ambiguous")


def test_get_results_json_success(
    client: TestClient,
    set_session_override: SessionOverrideSetter,
    monkeypatch: MonkeyPatch,
) -> None:
    set_session_override(FakeSession(results=[FakeResult(scalars_list=[123])]))

    monkeypatch.setattr(
        subcontest_routes,
        "get_results_payload",
        fake_get_results_payload,
    )

    resp = client.get("/contest/efo/2023-2024/lahtine/12.%20klass")
    assert resp.status_code == 200
    body = resp.json()
    assert body["contest_name"] == "Contest Name"
    assert body["columns"] == ["Task 1"]
    assert body["rows"][0]["person_name"] == "Alice"


def test_get_results_csv_success(
    client: TestClient,
    set_session_override: SessionOverrideSetter,
    monkeypatch: MonkeyPatch,
) -> None:
    set_session_override(FakeSession(results=[FakeResult(scalars_list=[123])]))

    monkeypatch.setattr(
        subcontest_routes,
        "get_results_payload",
        fake_get_results_payload,
    )

    resp = client.get(
        "/contest/efo/2023-2024/lahtine/12.%20klass",
        params={"format": "csv"},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    assert "subcontest_123_results.csv" in resp.headers["content-disposition"]
    assert resp.text.splitlines()[0].startswith("Koht,Nimi")


def test_get_subcontest_by_id_422_on_non_positive(client: TestClient) -> None:
    resp = client.get("/subcontests/0")
    assert resp.status_code == 422


def test_get_subcontest_by_id_404_from_service(
    client: TestClient,
    set_session_override: SessionOverrideSetter,
    monkeypatch: MonkeyPatch,
) -> None:
    set_session_override(FakeSession(results=[]))

    def raise_404(*, subcontest_id: int, session: object) -> None:
        _ = (subcontest_id, session)
        raise HTTPException(status_code=404, detail="Subcontest not found")

    monkeypatch.setattr(subcontest_routes, "get_results_payload", raise_404)

    resp = client.get("/subcontests/123")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Subcontest not found"


def test_get_subcontest_by_id_json_success(
    client: TestClient,
    set_session_override: SessionOverrideSetter,
    monkeypatch: MonkeyPatch,
) -> None:
    set_session_override(FakeSession(results=[]))

    monkeypatch.setattr(
        subcontest_routes,
        "get_results_payload",
        fake_get_results_payload,
    )

    resp = client.get("/subcontests/123")
    assert resp.status_code == 200
    assert resp.json()["year"] == 2023


def test_get_subcontest_by_id_csv_success(
    client: TestClient,
    set_session_override: SessionOverrideSetter,
    monkeypatch: MonkeyPatch,
) -> None:
    set_session_override(FakeSession(results=[]))

    monkeypatch.setattr(
        subcontest_routes,
        "get_results_payload",
        fake_get_results_payload,
    )

    resp = client.get("/subcontests/123", params={"format": "csv"})
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    assert "subcontest_123_results.csv" in resp.headers["content-disposition"]
