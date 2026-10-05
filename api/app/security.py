from __future__ import annotations

import os
import secrets
from typing import Annotated

from fastapi import Header, HTTPException


def require_internal_api(
    token: Annotated[str | None, Header(alias="X-EOA-Internal-Token")] = None,
) -> None:
    expected = os.getenv("EOA_INTERNAL_API_TOKEN")
    if expected and not secrets.compare_digest(token or "", expected):
        raise HTTPException(status_code=404, detail="Not found")
