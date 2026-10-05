from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    db_connection: str
    db_host: str
    db_port: int
    db_database: str
    db_username: str
    db_password: str

    @property
    def database_url(self) -> str:
        connection = self.db_connection.lower()
        driver = "mysql+pymysql" if connection in {"mariadb", "mysql"} else connection
        return URL.create(
            drivername=driver,
            username=self.db_username,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_database,
        ).render_as_string(hide_password=False)


settings = Settings(
    db_connection=os.getenv("DB_CONNECTION", "mariadb"),
    db_host=os.getenv("DB_HOST", "localhost"),
    db_port=int(os.getenv("DB_PORT", "3306")),
    db_database=os.getenv("DB_DATABASE", ""),
    db_username=os.getenv("DB_USERNAME", ""),
    db_password=os.getenv("DB_PASSWORD", ""),
)
