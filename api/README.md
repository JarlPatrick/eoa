## Endpoints

## Dev

To install dependencies:

```sh
uv sync --locked
```

To run checks:

```sh
cd api
uv run ruff format .
uv run ruff check .
uv run ty check .
```

To run tests:

```sh
cd api
uv run pytest
```

To run API in dev mode:

```sh
cd api
uv run fastapi dev
```

### Subcontest tree (each endpoint goes one level deeper)

- `GET /contest` → subjects (abbrev + full name)
- `GET /contest/{subject}` → seasons (format `YYYY-YYYY`)
- `GET /contest/{subject}/{season}` → contest types
- `GET /contest/{subject}/{season}/{type}` → age groups
- `GET /contest/{subject}/{season}/{type}/{age_group}` → results (`format=json|csv`)
- `GET /subcontests/{subcontest_id}` → results (`format=json|csv`)

Examples:

```bash
curl 'http://localhost:8000/contest' | jq
curl 'http://localhost:8000/contest/efo' | jq
curl 'http://localhost:8000/contest/efo/2023-2024' | jq
curl 'http://localhost:8000/contest/efo/2023-2024/lahtine' | jq
curl 'http://localhost:8000/contest/efo/2023-2024/lahtine/12.%20klass' | jq
curl -L 'http://localhost:8000/contest/efo/2023-2024/lahtine/12.%20klass?format=csv'
curl 'http://localhost:8000/subcontests/1' | jq
```

`/subjects` was removed; use `GET /contest` for the subject list (abbrev + full name).

### People

- `GET /contestant/{person_id}`
- `GET /mentor/{person_id}`
- `GET /people/search?q=...&role=student|mentor&offset=0&limit=20` (check `X-Result-Total` and `X-Result-Next-Offset`)

### Schools

- `GET /schools` (returns `school_id` + `school_name`)
- `GET /schools/search?q=...&offset=0&limit=20` (returns `school_id` + `school_name`; check `X-Result-Has-More` / `X-Result-Next-Offset`)
- `GET /schools/{school_id}/students`
- `GET /schools/{school_id}/mentors` (counts distinct students mentored, including students not shown by name)

### Internal site data

- `GET /statistics/students`
- `GET /statistics/students?weighted=true`
- `GET /statistics/students?format=csv`
- `GET /statistics/mentors`
- `GET /site/home` → public counts and latest-season results
- `GET /site/contests?subject=efo` → entries for one subject
- `GET /site/contests?q=...&offset=0&limit=20` → paged competition search
- `GET /site/schools` → school rankings based on students

These routes and `/health` are omitted from OpenAPI. In Docker Compose they require
the `X-EOA-Internal-Token` header from the Next.js server. The public `/api/*`
proxy rejects them. The only documentation page is `/api-reference` on the site;
FastAPI's built-in `/docs` and `/redoc` pages are disabled.

The Next.js site in `../web/` calls internal routes on the private Docker network.
The public `/api/*` proxy allows the documented contest, people, and school endpoints.
The Python package uses uv's build backend; `uv build --wheel` verifies the
package layout. The Docker image installs production dependencies directly from
`pyproject.toml` and `uv.lock` with `uv sync --locked --no-dev`.
