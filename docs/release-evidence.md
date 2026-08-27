# Release Evidence — Task Tracker API

## Project Identity

**Repository:** task-tracker-api  
**Branch:** final-project  
**Stack:** Python 3.11 · FastAPI · Pydantic v2 · pytest · Docker · GitHub Actions  

---

## 1. Test Suite Results

All tests pass. Command:

```bash
pytest tests/ -v
```

Output (run 2026-08-27):

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.3.2, pluggy-1.6.0
rootdir: /Users/macuser/Desktop/aub course/task-tracker-api
configfile: pytest.ini
plugins: anyio-4.12.1
collecting ... collected 40 items

tests/test_tasks.py::test_create_task_valid_returns_201_with_full_body PASSED
tests/test_tasks.py::test_create_task_missing_title_returns_422 PASSED
tests/test_tasks.py::test_create_task_blank_title_returns_422 PASSED
tests/test_tasks.py::test_create_task_invalid_priority_returns_422 PASSED
tests/test_tasks.py::test_create_task_unknown_field_returns_422 PASSED
tests/test_tasks.py::test_list_tasks_empty_returns_200_and_empty_list PASSED
tests/test_tasks.py::test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list PASSED
tests/test_tasks.py::test_list_tasks_filter_by_priority_returns_only_matches PASSED
tests/test_tasks.py::test_get_task_by_id_returns_task PASSED
tests/test_tasks.py::test_get_task_by_id_not_found_returns_404_with_detail PASSED
tests/test_tasks.py::test_patch_partial_update_keeps_other_fields PASSED
tests/test_tasks.py::test_patch_not_found_returns_404 PASSED
tests/test_tasks.py::test_patch_valid_transition_todo_to_inprogress_returns_200 PASSED
tests/test_tasks.py::test_patch_invalid_transition_todo_to_done_returns_422 PASSED
tests/test_tasks.py::test_patch_same_status_returns_422 PASSED
tests/test_tasks.py::test_patch_valid_transition_inprogress_to_done_returns_200 PASSED
tests/test_tasks.py::test_patch_valid_transition_done_to_inprogress_returns_200 PASSED
tests/test_tasks.py::test_patch_whitespace_only_title_returns_422 PASSED
tests/test_tasks.py::test_patch_invalid_priority_value_returns_422 PASSED
tests/test_tasks.py::test_patch_empty_body_returns_200_with_fields_unchanged PASSED
tests/test_tasks.py::test_patch_unknown_field_returns_422 PASSED
tests/test_tasks.py::test_delete_existing_returns_204_no_body PASSED
tests/test_tasks.py::test_delete_missing_returns_404 PASSED
tests/test_tasks.py::test_create_task_with_tags_returns_201_and_tags_in_response PASSED
tests/test_tasks.py::test_create_task_with_empty_string_tag_returns_422 PASSED
tests/test_tasks.py::test_create_task_with_whitespace_only_tag_returns_422 PASSED
tests/test_tasks.py::test_create_task_with_too_many_tags_returns_422 PASSED
tests/test_tasks.py::test_create_task_with_no_tags_defaults_to_empty_list PASSED
tests/test_tasks.py::test_patch_task_tags_preserves_other_fields PASSED
tests/test_tasks.py::test_patch_task_tags_can_be_cleared PASSED
tests/test_tasks.py::test_patch_unrelated_update_preserves_tags PASSED
tests/test_tasks.py::test_list_tasks_filter_by_tag_returns_only_matching PASSED
tests/test_tasks.py::test_list_tasks_filter_by_tag_no_match_returns_empty_list PASSED
tests/test_tasks.py::test_list_tasks_filter_by_tag_is_case_insensitive PASSED
tests/test_tasks.py::test_list_tasks_search_by_title_returns_matching PASSED
tests/test_tasks.py::test_list_tasks_search_by_description_returns_matching PASSED
tests/test_tasks.py::test_list_tasks_search_is_case_insensitive PASSED
tests/test_tasks.py::test_list_tasks_search_no_match_returns_200_empty_list PASSED
tests/test_tasks.py::test_list_tasks_combined_search_and_status_filter PASSED
tests/test_tasks.py::test_list_tasks_combined_tag_and_priority_filter PASSED

============================== 40 passed in 0.09s ==============================
```

**Coverage:** All five CRUD routes; all filter parameters (`status`, `priority`, `q`, `tag`); valid and invalid status transitions (including same-status and skip-step); tag operations (set, clear, preserve on unrelated patch); combined multi-filter queries; and strict validation (blank title, unknown fields, invalid enum values, tag constraints).

Test isolation: the `_reset_storage` autouse fixture in `tests/conftest.py` resets the in-memory store before every test so tests are fully order-independent.

---

## 2. Docker Build

Single-stage build using `python:3.11-slim`:

```bash
docker build -t task-tracker-api .
```

Build completes without warnings or errors. The `data/` directory (runtime data) is excluded via `.dockerignore` so no runtime state is baked into the image.

Full stack via docker-compose:

```bash
docker compose up -d
curl http://localhost:8000/health
# {"status":"ok","timestamp":"2025-08-01T12:00:00Z"}
```

The compose file starts two services: `api` (FastAPI on :8000) and `frontend` (nginx on :5500). The `frontend` service has `depends_on: condition: service_healthy` so nginx does not start until the API health check passes.

---

## 3. CI Pipeline

Workflow file: `.github/workflows/ci.yml`  
Trigger: every push to any branch.

| Job | What runs | Pass condition |
|-----|-----------|----------------|
| `test` | `pytest tests/ -v` on Python 3.11 | All 40 tests pass |
| `docker` | `docker build`, start container, `curl --fail http://localhost:8000/health` | HTTP 200 from health endpoint |

The `docker` job declares `needs: test`, so it only runs after the test job succeeds. A test failure prevents the Docker build from running.

---

## 4. Health Endpoint

```
GET /health  →  200 OK
{"status": "ok", "timestamp": "<ISO 8601>"}
```

Used in three places:
- docker-compose health check (determines when nginx may start)
- CI smoke test (`curl --fail`)
- Manual verification during development

---

## 5. Architecture Decisions

Six ADRs recorded in `docs/release-evidence.md` (this file) and `AGENTS.md`:

| ADR | Decision | Rationale |
|-----|----------|-----------|
| ADR-001 | In-memory `dict` storage | Scope: learning project; no DB provisioning needed |
| ADR-002 | Pydantic v2 + `extra="forbid"` | Strict validation; rejects unknown fields with 422 |
| ADR-003 | Status transitions in `business_rules.py` | Keeps router thin; rule testable in isolation |
| ADR-004 | CORS hard-coded to `localhost:5500` | Avoids accidental `*` wildcard; local-only project |
| ADR-005 | Single-stage Docker build | No compiled artifact; no multi-stage needed |
| ADR-006 | pytest + TestClient | Full request/response cycle; no live server needed |

---

## 6. Security Posture Summary

Full findings in `docs/final-ai-review.md` (section 2). No critical or high-severity issues.

| Finding | Severity | Status |
|---------|----------|--------|
| CORS hard-coded | Low | By design; documented |
| No authentication | Medium | Known limitation; out of scope |
| In-memory storage | Low | By design |
| No rate limiting | Low | Out of scope for local use |
| No description length cap | Low | Known limitation |
| No secrets in repo | — | Pass |
| XSS protection in frontend | — | Pass — `escape()` function verified |

---

## 7. Known Limitations

Documented in README.md; accepted for a learning project:

- Storage is in-memory only — data is lost on restart.
- No authentication or authorization.
- CORS is hard-coded to `http://localhost:5500`.
- No rate limiting.
- `description` field has no server-side length cap.
