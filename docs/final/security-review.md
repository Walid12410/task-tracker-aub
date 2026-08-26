# Security Review — Task Tracker API

**Reviewed:** Final project phase  
**Scope:** `app/` source code, `Dockerfile`, `docker-compose.yml`, `.gitignore`, `.env.example`  
**Method:** Static analysis assisted by Claude Code; each finding verified manually.

---

## Findings

### SEC-001: CORS locked to a single origin (Low risk — by design)

**Location:** `app/main.py:22–27`

**Description:** `allow_origins` is hard-coded to `["http://localhost:5500"]`. This is intentional for a local development project and is not a wildcard (`*`), so it does not expose the API to arbitrary origins.

**Risk:** If the frontend is ever served from a different origin without updating this list, the browser will block requests. Not a security vulnerability — the restriction is correct.

**Recommendation:** Document the limitation (done in README). For a production deployment, read the allowed origins from an environment variable.

---

### SEC-002: No authentication or authorization (Medium risk — known limitation)

**Location:** All routes in `app/main.py`

**Description:** Any client can create, update, or delete any task. There is no API key, JWT, or session mechanism.

**Risk:** In a multi-user or internet-exposed deployment, any user could modify or delete another user's tasks.

**Recommendation:** Acceptable for a local learning project. A production version would add an auth middleware (e.g., OAuth2 with JWT via `fastapi.security`).

---

### SEC-003: In-memory storage — no persistence, no multi-process safety (Low risk — by design)

**Location:** `app/storage.py`

**Description:** All tasks are stored in a module-level dict. If multiple worker processes are started (e.g., `uvicorn --workers 4`), each process has its own copy and writes do not propagate across processes.

**Risk:** Data loss on restart; inconsistent state with multiple workers.

**Recommendation:** Documented in README. Acceptable for the current project scope. A production system would use a database.

---

### SEC-004: No rate limiting (Low risk for local use)

**Location:** `app/main.py` — all routes

**Description:** The API accepts unlimited requests per second with no throttling.

**Risk:** A client can flood the server with requests, consuming CPU/memory. For a local development server this is not a concern. Exposing the API publicly without rate limiting would be a problem.

**Recommendation:** For public deployment, add a middleware such as `slowapi`. Not required for this project.

---

### SEC-005: `description` field has no server-side length cap

**Location:** `app/models.py` — `TaskCreate.description`, `TaskUpdate.description`

**Description:** `title` is validated to 200 characters max, but `description` has no length limit.

**Risk:** A client can POST arbitrarily large description strings, consuming memory proportional to input size.

**Recommendation:** Add a `@field_validator("description")` that caps at, e.g., 2000 characters. Low priority for a local project.

---

### SEC-006: Secrets — no real secrets in the repository (Pass)

**Checked:**
- `.gitignore` excludes `.env`, `venv/`, and `*.log`
- `.env.example` contains only non-sensitive defaults (`PORT=8000`, `APP_ENV=development`)
- `Dockerfile` does not `COPY .env` or embed any credentials
- `docker-compose.yml` uses environment variables, not hardcoded secrets

**Result:** No credentials, tokens, or real secrets found in the repository.

---

### SEC-007: XSS protection in frontend (Pass)

**Location:** `frontend/index.html` — `escape()` function and all `innerHTML` assignments

**Description:** All user-controlled strings (task title, description, tags, assignee) are passed through the `escape()` function before being inserted into the DOM via `innerHTML`. This converts `<`, `>`, `&`, and `"` to their HTML entities.

**Result:** No reflected or stored XSS vector found in the frontend.

---

## Summary

| ID | Finding | Severity | Disposition |
|----|---------|----------|-------------|
| SEC-001 | CORS hard-coded | Low | Acceptable; documented |
| SEC-002 | No authentication | Medium | Known limitation; out of scope |
| SEC-003 | In-memory storage | Low | By design |
| SEC-004 | No rate limiting | Low | Out of scope for local use |
| SEC-005 | Description no length cap | Low | Known limitation |
| SEC-006 | No secrets in repo | — | Pass |
| SEC-007 | XSS in frontend | — | Pass |

No critical or high-severity issues found. The application is appropriate for local development and learning use.
