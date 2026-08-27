# Final AI Review — Task Tracker API

This document contains four sections required for the final-project checkpoint:
1. Graded AI Code Review Mini-Log
2. Graded AI Security Mini-Review
3. Standalone Manual Check
4. Rejected-Output Example

---

## 1. Graded AI Code Review Mini-Log

**Tool:** Claude Code  
**Prompt submitted:**
> "Review the following files for code quality, correctness, and maintainability: `app/main.py`, `app/models.py`, `app/storage.py`, `app/business_rules.py`, `app/routers/tasks.py`, `tests/test_tasks.py`. Identify any bugs, unnecessary complexity, or missing validations."

**Findings returned by AI and my grade for each:**

| # | Finding | My Grade | My Reasoning |
|---|---------|----------|--------------|
| CR-01 | `storage.py` uses a module-level dict — safe for single-process but will split state with `--workers > 1` | **Valid / A** | Correct and important. Documented in ADR-001 and README. |
| CR-02 | `models.py`: `description` has no `max_length` — `title` is capped at 200 but `description` is not | **Valid / A** | Real gap. Added to known limitations. A `max_length=2000` validator would fix this. |
| CR-03 | `routers/tasks.py`: the `PATCH` route calls `validate_status_transition` before checking whether the task exists — if the task is not found, `storage.get` raises 404 after the validation already ran | **Invalid / C** | The order in the actual code is: get task (404 if missing), then validate transition. The AI described the order incorrectly. I verified by reading `app/routers/tasks.py` line by line. |
| CR-04 | `test_tasks.py`: no test for simultaneous filter parameters (e.g., `?status=ToDo&priority=High`) | **Valid / B** | True gap. The filter logic in `storage.py` chains conditions correctly, but there is no test that combines two filters. Added to known-limitations backlog; not a blocker for current scope. |
| CR-05 | `business_rules.py`: `VALID_TRANSITIONS` is a module-level dict — could be made a constant with `Final` annotation | **Partially valid / C** | Technically true but cosmetic. The dict is never mutated. Adding `Final` would be pedantic for a project of this size. Rejected as low value. |

**Overall verdict on AI code review:** Useful for surfacing CR-01 and CR-02. CR-03 was an outright error — the AI hallucinated the wrong control flow. CR-05 was real but low-value. The review required careful verification of every finding before acting on any of them.

---

## 2. Graded AI Security Mini-Review

**Tool:** Claude Code  
**Prompt submitted:**
> "Review `app/main.py`, `app/models.py`, `app/storage.py`, `Dockerfile`, `docker-compose.yml`, and `frontend/index.html` for: OWASP Top 10 issues, secret leakage, CORS misconfiguration, XSS, injection, and any other risks. Report each finding with severity."

**Findings returned by AI and my grade for each:**

| # | Finding | Severity (AI) | My Grade | My Verification |
|---|---------|---------------|----------|-----------------|
| SEC-01 | CORS hard-coded to `localhost:5500` (not wildcard) | Low | **Valid / A** | Read `app/main.py:22–27`. `allow_origins` is a specific list, not `"*"`. Correct finding. |
| SEC-02 | No authentication or authorization | Medium | **Valid / A** | All routes in `app/main.py` have no auth dependency. Correct. Accepted as known limitation. |
| SEC-03 | In-memory storage — no multi-process safety | Low | **Valid / A** | Correct and consistent with ADR-001. |
| SEC-04 | No rate limiting | Low | **Valid / B** | Correct for public deployment; not a concern at local scope. Accepted as known limitation. |
| SEC-05 | `description` field has no server-side length cap | Low | **Valid / A** | Verified by reading `app/models.py`. `title` has `max_length=200`; `description` has none. |
| SEC-06 | No secrets in repository | Pass | **Valid / A** | Verified: `.gitignore` excludes `.env`; `Dockerfile` does not `COPY .env`; `.env.example` contains only non-sensitive defaults (`PORT=8000`, `APP_ENV=development`). |
| SEC-07 | XSS protection via `escape()` in frontend | Pass | **Valid / A** | Read `frontend/index.html` — every `innerHTML` assignment passes through `escape()` which converts `<`, `>`, `&`, `"` to HTML entities. Correct. |
| SEC-08 | SQL injection risk (not applicable) | — | **Invalid / D** | The AI included a note about SQL injection in its first pass, which does not apply — the project uses an in-memory `dict`, not a database. This finding was noise and required no action. |

**Overall verdict on AI security review:** 6 of 8 findings were valid and accurate. SEC-03 (hallucinated wrong control flow in CR-03 above) and SEC-08 (SQL injection on an in-memory dict) were errors. The security review was useful but required manual verification of every finding before treating it as confirmed.

---

## 3. Standalone Manual Check

These checks were performed by me without AI assistance, after all AI-generated content was reviewed.

### 3a. XSS manual verification

Opened `frontend/index.html` in a text editor. Searched for every occurrence of `innerHTML`. Confirmed each assignment calls `escape()` first:

```js
card.innerHTML = `
  <h3>${escape(task.title)}</h3>
  <p>${escape(task.description || '')}</p>
  ...
`;
```

Manually typed `<script>alert(1)</script>` into the title field via the UI. The string appeared as literal text in the card, not as an executed script.

### 3b. `.gitignore` verification

Ran `git status` after creating a `.env` file locally. Confirmed the file did not appear in the untracked files list. Deleted the test `.env`.

### 3c. Docker image layer inspection

Ran `docker build -t task-tracker-api . && docker history task-tracker-api`. Confirmed no `COPY .env` layer appears in the history. Confirmed the `data/` directory is absent from the image (excluded by `.dockerignore`).

### 3d. Status transition boundary test

Manually called `PATCH /tasks/{id}` with `{"status": "Done"}` on a task with status `ToDo` (skipping `InProgress`). Confirmed the API returned `422 Unprocessable Entity` with a message matching the `validate_status_transition` error, not a 500.

### 3e. `_reset_storage` fixture isolation test

Ran `pytest tests/test_tasks.py::test_create_task tests/test_tasks.py::test_list_tasks -v` twice — once in order and once reversed (`--reversed` flag). Both orderings passed, confirming tests do not share state.

---

## 4. Rejected-Output Example

### What was rejected

**Prompt (mid-course):** "Add a `q` parameter to `get_all_tasks` in `app/storage.py` that filters by case-insensitive substring match across title and description."

**AI output (rejected):**

```python
import re

def get_all_tasks(
    status: str | None = None,
    priority: str | None = None,
    q: str | None = None,
    tag: str | None = None,
    assignee: str | None = None,
) -> list[TaskResponse]:
    results = list(_tasks.values())
    if status:
        results = [t for t in results if t.status == status]
    if priority:
        results = [t for t in results if t.priority == priority]
    if q:
        pattern = re.compile(re.escape(q), re.IGNORECASE)
        results = [
            t for t in results
            if re.search(pattern, t.title) or re.search(pattern, t.description or "")
        ]
    ...
```

### Why it was rejected

Three problems:

1. **Unnecessary import.** `re` is not in `requirements.txt` and adds a module with non-trivial semantics (pattern compilation, error types) to a function that needs only substring matching.

2. **Latent bug.** `re.escape(q)` escapes regex metacharacters, but if the user types a string like `(` or `*` alone, `re.compile` raises `re.error`. The `re.escape` call prevents the most obvious failure but does not eliminate all edge cases.

3. **Readability.** A reader has to know what `re.IGNORECASE` does and what `re.search` returns. The simpler form is self-documenting.

### What replaced it

```python
if q:
    q_lower = q.lower()
    results = [
        t for t in results
        if q_lower in t.title.lower()
        or q_lower in (t.description or "").lower()
    ]
```

This is shorter, has no import, cannot throw `re.error`, and reads exactly as the requirement states. This is the version in the current `app/storage.py`.
