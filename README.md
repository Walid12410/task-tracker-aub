# Task Tracker API

A REST API for managing tasks, built with Python and FastAPI. Features a JSON-backed in-memory store, a vanilla JavaScript Kanban board frontend, and a full pytest suite. Containerized with Docker and continuously verified by GitHub Actions.

## Architecture

```
task-tracker-api/
├── app/
│   ├── main.py            # FastAPI app, route definitions, CORS
│   ├── models.py          # Pydantic request/response models
│   ├── storage.py         # In-memory task store (dict + uuid)
│   ├── business_rules.py  # Status transition validation
│   └── routers/           # Router module (prefix /tasks)
├── frontend/
│   └── index.html         # Vanilla JS Kanban board
├── tests/
│   ├── conftest.py        # Shared fixtures (TestClient, storage reset)
│   └── test_tasks.py      # Full route coverage (CRUD + tags + search)
├── docs/
│    # Final-project docs (ADR, security, reflection)
├── Dockerfile
├── docker-compose.yml
├── .github/workflows/ci.yml
├── AGENTS.md              # AI governance log
└── requirements.txt
```

## Quick Start (Docker)

```bash
docker compose up
```

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Frontend: http://localhost:5500

## Quick Start (local)

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Serve the frontend in a second terminal:

```bash
python -m http.server 5500 --directory frontend
```

Open http://localhost:5500.

## Environment Variables

Copy `.env.example` to `.env` before running locally:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Port uvicorn listens on |
| `APP_ENV` | `development` | Runtime environment label |

## API Reference

### Health

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Returns `{"status":"ok","timestamp":"..."}` |

### Tasks

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/tasks` | List tasks (filterable) |
| `POST` | `/tasks` | Create a task |
| `GET` | `/tasks/{id}` | Get a single task |
| `PATCH` | `/tasks/{id}` | Partial update |
| `DELETE` | `/tasks/{id}` | Delete a task |

#### Filter parameters for `GET /tasks`

| Parameter | Type | Example |
|-----------|------|---------|
| `status` | `ToDo` \| `InProgress` \| `Done` | `?status=InProgress` |
| `priority` | `Low` \| `Medium` \| `High` | `?priority=High` |
| `q` | string | `?q=login` (searches title + description) |
| `tag` | string | `?tag=backend` (case-insensitive) |
| `assignee` | string | `?assignee=Alice` |

#### Task object

```json
{
  "id": "uuid",
  "title": "string (1–200 chars)",
  "description": "string",
  "status": "ToDo | InProgress | Done",
  "priority": "Low | Medium | High",
  "assignee": "string | null",
  "tags": ["string"],
  "created_at": "ISO 8601",
  "updated_at": "ISO 8601"
}
```

#### Status transitions

Only these moves are allowed via `PATCH`:

- `ToDo → InProgress`
- `InProgress → Done`
- `Done → InProgress`

Any other transition returns `422 Unprocessable Entity`.

## Running Tests

```bash
pytest tests/ -v
```

All tests use an isolated in-memory store that resets between each test via the `_reset_storage` autouse fixture.

## CI

GitHub Actions runs on every push:

1. **test** — installs Python 3.11, runs `pytest tests/ -v`
2. **docker** — builds the image and smoke-tests `GET /health`

See `.github/workflows/ci.yml`.

## AI Governance

All AI tool usage is documented in `AGENTS.md`. Every AI-generated output was reviewed line-by-line and tested before commit. No AI output was committed without passing the full test suite.

## Known Limitations

- Storage is in-memory only — data is lost on restart and not suitable for multi-process deployment.
- No authentication or authorization.
- CORS is hard-coded to `http://localhost:5500`. Change `allow_origins` in `app/main.py` for other environments.
- No rate limiting.
- `description` field has no server-side length cap (only `title` is length-validated).

## Final Project

The final-project hardening phase added containerization, CI, security documentation, and AI governance on top of the working mid-course API. No new product features were added; the goal was operational completeness.

| Deliverable | Location |
|-------------|----------|
| Release evidence (tests, Docker, CI) | `docs/release-evidence.md` |
| AI code review and security mini-log | `docs/final-ai-review.md` |
| AI governance playbook | `docs/ai-playbook.md` |
| AI governance log | `AGENTS.md` |

All AI-generated content was reviewed line-by-line and tested before commit. The rejected regex search implementation is documented as the canonical rejected-output example in `docs/final-ai-review.md`.
