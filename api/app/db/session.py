from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

if TYPE_CHECKING:
    from collections.abc import Generator

    from sqlalchemy.orm import Session

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_session() -> Generator[Session]:
    with SessionLocal() as session:
        yield session
