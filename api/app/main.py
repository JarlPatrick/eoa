from fastapi import Depends, FastAPI

from app.routes.people import router as people_router
from app.routes.schools import router as schools_router
from app.routes.site import router as site_router
from app.routes.statistics import router as statistics_router
from app.routes.subcontest import router as subcontest_router
from app.schemas import HealthResponse
from app.security import require_internal_api

app = FastAPI(
    title="EOA API",
    servers=[{"url": "/api", "description": "Veebilehe API"}],
    docs_url=None,
    redoc_url=None,
)

app.include_router(subcontest_router)
app.include_router(people_router)
app.include_router(schools_router)
app.include_router(site_router, include_in_schema=False)
app.include_router(statistics_router, include_in_schema=False)


@app.get(
    "/health",
    response_model=HealthResponse,
    include_in_schema=False,
    dependencies=[Depends(require_internal_api)],
)
def health() -> dict[str, str]:
    return {"status": "ok"}
