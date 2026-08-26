# Architecture Decision Records — Final Project

## ADR-001: In-memory storage over a database

**Status:** Accepted

**Context:** The project is a learning exercise. Adding a database server (PostgreSQL, SQLite) would require connection pooling, migrations, and environment provisioning that shifts focus away from API design and testing.

**Decision:** Use a plain Python `dict` (`_tasks: dict[str, TaskResponse]`) as the data store. A `_reset()` function enables deterministic test isolation without mocking.

**Consequences:**
- Data is lost on restart. Acceptable for a learning project; documented in README known limitations.
- Tests are fast and do not require a running database.
- Cannot scale beyond a single process. Acceptable for current scope.

---

## ADR-002: Pydantic v2 for request/response validation

**Status:** Accepted

**Context:** FastAPI supports both Pydantic v1 and v2. v2 is the current release and uses `model_config = ConfigDict(...)` instead of the older `class Config`.

**Decision:** Use Pydantic v2 throughout. All models use `ConfigDict(extra="forbid")` to reject unknown fields and return `422` instead of silently ignoring unexpected input.

**Consequences:**
- Unknown fields in request bodies return `422`, which is the correct behavior for a strict API.
- Field validators use the `@field_validator` decorator with `@classmethod`, which is the v2 pattern.

---

## ADR-003: Status transition enforcement in the service layer

**Status:** Accepted

**Context:** The task lifecycle has a defined flow: `ToDo → InProgress → Done`, with `Done → InProgress` allowed for re-opening. Enforcing this in the router vs. a dedicated function was considered.

**Decision:** Enforce transitions in `app/business_rules.py` via `validate_status_transition`. The router calls this function before calling storage. This keeps the router thin and the rule testable in isolation.

**Consequences:**
- Adding or removing a transition requires changing only `VALID_TRANSITIONS` in `business_rules.py`.
- The router raises `HTTPException(422)` on invalid transitions, consistent with validation errors.

---

## ADR-004: CORS hard-coded to localhost:5500

**Status:** Accepted with known limitation

**Context:** The frontend is served from `http://localhost:5500`. CORS must allow this origin so the browser does not block fetch calls to the API at port 8000.

**Decision:** Hard-code `allow_origins=["http://localhost:5500"]` in `app/main.py`. A configurable origin list via environment variable was considered but adds complexity not justified for a local-only project.

**Consequences:**
- Deploying to any other domain requires a code change. Documented in README.
- No risk of accidentally opening CORS to `*` in production.

---

## ADR-005: Docker and docker-compose for containerization

**Status:** Accepted (final project)

**Context:** The assignment requires Docker files. The app has no external dependencies (no database), so a single-stage Dockerfile is sufficient.

**Decision:** Single-stage `python:3.11-slim` image. `docker-compose.yml` adds a second service (nginx) to serve the frontend, with a health-check dependency so nginx does not start before the API is ready.

**Consequences:**
- `docker compose up` starts the full stack with one command.
- No multi-stage build needed because there is no compiled artifact to separate from the runtime.
- Environment variables are injected via `docker-compose.yml`; `.env` is never baked into the image.

---

## ADR-006: pytest with TestClient for integration tests

**Status:** Accepted

**Context:** The tests exercise the HTTP layer (routes, status codes, response bodies), not individual functions. Using `TestClient` from `httpx` means tests run synchronously without a live server, which is fast and CI-friendly.

**Decision:** All tests use `TestClient(app)` provided by the `client` fixture in `conftest.py`. The `_reset_storage` autouse fixture resets state before and after every test, so tests are order-independent.

**Consequences:**
- Tests cover the full request/response cycle including Pydantic validation and business rules.
- No mocking of internal functions — the real storage is used, which means tests would catch any regression in the storage layer.
