from __future__ import annotations

from app.schemas import ResultsPayload
from app.services.results import payload_as_csv


def test_payload_as_csv_minimal_headers_and_padding() -> None:
    payload = ResultsPayload.model_validate(
        {
            "title": "",
            "contest_name": "C",
            "subcontest": None,
            "age_group": None,
            "contest": None,
            "year": None,
            "subject": None,
            "type": None,
            "columns": ["T1", "T2", "T3"],
            "rows": [
                {
                    "placement": 1,
                    "person_name": "Alice",
                    "age_group": "",
                    "school": "",
                    "mentors": [],
                    "fields": ["10"],
                }
            ],
        }
    )

    resp = payload_as_csv(subcontest_id=5, payload=payload)
    assert resp.headers["content-type"].startswith("text/csv")
    assert "subcontest_5_results.csv" in resp.headers["content-disposition"]

    lines = bytes(resp.body).decode("utf-8").splitlines()
    assert lines[0] == "Koht,Nimi,T1,T2,T3"
    assert lines[1] == "1,Alice,10,,"


def test_payload_as_csv_includes_optional_columns_when_present() -> None:
    payload = ResultsPayload.model_validate(
        {
            "title": "",
            "contest_name": "C",
            "subcontest": None,
            "age_group": None,
            "contest": None,
            "year": None,
            "subject": None,
            "type": None,
            "columns": [],
            "rows": [
                {
                    "placement": None,
                    "person_name": "Bob",
                    "age_group": "10. klass",
                    "school": "School",
                    "mentors": ["Mentor A", "Mentor B"],
                    "fields": [],
                }
            ],
        }
    )

    resp = payload_as_csv(subcontest_id=1, payload=payload)
    lines = bytes(resp.body).decode("utf-8").splitlines()
    assert lines[0] == "Koht,Nimi,Klass,Kool,Juhendaja"
    assert lines[1] == ",Bob,10. klass,School,Mentor A / Mentor B"
