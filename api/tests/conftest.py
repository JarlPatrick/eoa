from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from fastapi import FastAPI

    from .fakes import FakeSession

API_DIR = Path(__file__).resolve().parents[1]
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))


@pytest.fixture
def fastapi_app() -> Generator[FastAPI]:
    from app.main import app

    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def client(fastapi_app: FastAPI) -> Generator[TestClient]:
    with TestClient(fastapi_app) as c:
        yield c


@pytest.fixture
def set_session_override(
    fastapi_app: FastAPI,
) -> Callable[[FakeSession], None]:
    from app.db import get_session

    def _set(fake_session: FakeSession) -> None:
        def override_get_session() -> Generator[FakeSession]:
            yield fake_session

        fastapi_app.dependency_overrides[get_session] = override_get_session

    return _set
