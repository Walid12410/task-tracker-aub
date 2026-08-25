# Mini Architecture Decision Record — Mid-Course Project

## Context

Starting point: FastAPI backend with in-memory storage, Pydantic validation, five CRUD routes for tasks, and a single vanilla-JS Kanban board frontend. No database. 23 existing passing tests.

---

## Feature 1: Tags / Labels

### Decision: list[str] field on the task model

Tags are stored as `list[str]` directly on `TaskResponse`. No separate collection or join table.

**Why:** The persistence layer is in-memory. A separate dict of tags keyed by task id would add complexity with no benefit at this scale. Embedding tags in the task keeps the storage simple and consistent with how all other task fields work.

### Validation

- Each tag is stripped and checked non-empty.
- Maximum 10 tags per task, maximum 50 characters per tag.
- Validated in Pydantic `field_validator` on both `TaskCreate` and `TaskUpdate`.
- `TaskUpdate.tags` is `Optional[list[str]] = None` so omitting tags from a PATCH does not clear them.

### API changes

- `TaskCreate`, `TaskUpdate`, `TaskResponse` all gain a `tags` field.
- `GET /tasks` gains a `?tag=<value>` query parameter — case-insensitive exact match against the task's tag list.
- All other endpoints unchanged.

### Frontend changes

- Tags field added to the modal form (comma-separated input).
- `parseTags()` function splits, trims, and filters empty values before sending.
- `buildCard()` renders tag chips using `.card-tags` / `.tag-chip` CSS classes.
- Edit modal pre-fills the tags field by joining existing tags with `", "`.

### Alternatives considered and rejected

| Option | Verdict |
|---|---|
| Store tags as comma-separated string in a single field | Rejected — harder to validate per-tag, harder to filter, requires string parsing on every read |
| Separate `/tags` resource with its own CRUD routes | Rejected — overkill for this scope; adds 4+ new routes and a foreign-key relationship the in-memory store doesn't support cleanly |
| Maximum tag count of 5 | Rejected in favor of 10 — 5 felt too restrictive for realistic use without adding safety |
| Case-sensitive tag matching | Rejected — "Frontend" and "frontend" should be the same tag to users |

### Files changed

| File | Change |
|---|---|
| `app/models.py` | Added `tags: list[str]` to `TaskCreate`/`TaskResponse`; `tags: Optional[list[str]]` to `TaskUpdate`; added `validate_tags` validators |
| `app/storage.py` | `add_task` stores `payload.tags`; `get_all_tasks` filters by `tag` param |
| `app/main.py` | `list_tasks` accepts `tag` param; seed data includes tags |
| `frontend/index.html` | Tags field in modal, tag chips on cards, tag filter in filter bar |
| `tests/test_tasks.py` | 11 new tests covering create/update/filter/validation |

---

## Feature 2: Search + Combined Filters

### Decision: backend filtering via query parameters

Text search and all filters are applied on the backend. The frontend always sends the current filter state as query parameters and re-renders the full response.

**Why:** The existing status and priority filters already use `GET /tasks?status=&priority=`. Adding search as another query parameter keeps the approach consistent. Frontend-only filtering was rejected because it breaks when tasks are paginated later and is inconsistent with the existing pattern.

### Search behavior

- Parameter: `?q=<term>`
- Matches if `term` appears (case-insensitive) in `title` or `description`.
- An empty or whitespace-only `q` is ignored (no filtering applied).
- Combined with all other filters using AND logic: each filter narrows the result set independently.

### New query parameters

| Parameter | Type | Behavior |
|---|---|---|
| `q` | `Optional[str]` | Case-insensitive substring match on title + description |
| `tag` | `Optional[str]` | Case-insensitive exact match against any tag in the task's tag list |
| `assignee` | `Optional[str]` | Exact string match on the assignee field |

### Frontend changes

- Filter bar added between the header and the board.
- Four controls: search input, status select, priority select, tag input, and a Clear button.
- Search and tag inputs use a 300 ms debounce to avoid a request on every keystroke.
- Status and priority selects fire immediately on change.
- `currentFilters` object tracks active state; `buildQueryString()` constructs the URL.
- `fetchTasks()` now reads `currentFilters` and appends query params.
- Clear button resets all controls and calls `fetchTasks()`.

### Alternatives considered and rejected

| Option | Verdict |
|---|---|
| Filter tasks on the frontend without calling the backend | Rejected — inconsistent with existing filter pattern; breaks with pagination |
| Separate `GET /tasks/search` endpoint | Rejected — adds an unnecessary route; query params on the existing endpoint are sufficient |
| OR logic between filters | Rejected — AND is the expected behavior when stacking filters |
| Live search on every keystroke (no debounce) | Rejected — would fire a request for every character; debounce at 300 ms keeps it responsive without excess requests |

### Files changed

| File | Change |
|---|---|
| `app/storage.py` | `get_all_tasks` gains `q`, `tag`, `assignee` parameters with AND filter logic |
| `app/main.py` | `list_tasks` route gains `q`, `tag`, `assignee` query params |
| `frontend/index.html` | Filter bar HTML + CSS; `currentFilters`, `buildQueryString`, `onFilterChange`, `onSearchInput` JS functions |
| `tests/test_tasks.py` | 6 new tests covering search by title, description, case-insensitivity, no-match, and combined filters |
