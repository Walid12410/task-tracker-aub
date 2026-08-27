# Prompt Log — Mid-Course Project

---

## Feature 1: Tags / Labels

---

### Prompt T-1 (Weak → Rewritten)

**Original weak prompt:**
> "Add tags to tasks"

**Why it was weak:** No constraints, no model detail, no validation rules, no frontend scope. The AI would guess the data type, validation limits, filter behavior, and UI placement — likely overbuilding or making incompatible choices.

**Rewritten strong prompt:**
> "Add a `tags` field to the existing Task Tracker FastAPI backend. Tags must be a list of strings. Each tag must be trimmed and non-empty — reject blank tags with 422. Limit to 10 tags per task, 50 characters per tag. Add the field to `TaskCreate`, `TaskUpdate` (Optional so omitting it in PATCH does not clear tags), and `TaskResponse`. Store tags in the existing in-memory dict — no new storage layer. Add a `?tag=` query parameter to `GET /tasks` for case-insensitive exact match filtering. Do not add authentication, pagination, or a separate tags resource."

**What AI returned:** Correct implementation across `models.py`, `storage.py`, `main.py`. Added `validate_tags` to both `TaskCreate` and `TaskUpdate`.

**Accepted:** Full implementation — data types, validators, storage changes, filter logic.

**Edited:** Changed seed data to include representative tags so the board shows chips immediately on startup.

**Rejected:** AI initially used a `Set[str]` to deduplicate tags automatically. I rejected this because sets are unordered and the JSON serialization is inconsistent. Changed to `list[str]` with no deduplication — the user controls what they enter.

---

### Prompt T-2

**Prompt:**
> "Add tag chips to existing task cards in `frontend/index.html`. Each chip should use class `tag-chip` inside a `card-tags` div. Render chips below the description and above the card-meta row. Do not render the `card-tags` div if the task has no tags. Reuse the existing blue color palette (#ebf4ff background, #2b6cb0 text). Do not break drag-and-drop or priority sorting."

**What AI returned:** Updated `buildCard()` with conditional `tagsHtml`, added `.card-tags` and `.tag-chip` CSS rules.

**Accepted:** Conditional rendering logic, CSS using existing color variables.

**Edited:** Adjusted font-size from 0.75rem to 0.68rem — the original was too large relative to the priority tag.

**Rejected:** Nothing rejected for this prompt.

---

### Prompt T-3

**Prompt:**
> "Add a Tags field to the existing create/edit modal in `frontend/index.html`. Use a single text input where users enter comma-separated tags. On form submit, split by comma, trim each, and filter empty strings before sending as a `tags` array. In edit mode, pre-fill the field by joining the task's existing tags with `', '`. Show validation errors from the server inside the existing form-error banner. Do not add a tag chip UI inside the modal itself."

**What AI returned:** Added `<input id="field-tags">` to the form, `parseTags()` helper, updated `openModal()` and submit handler.

**Accepted:** All of it — the approach is clean and consistent with the rest of the form.

**Edited:** Added `id="error-tags"` span below the field to match the pattern used for the title error — the AI omitted a per-field error slot for tags.

**Rejected:** AI suggested a chip-based tag input with add/remove buttons. Rejected as too complex for this scope — a comma-separated text input is simpler and sufficient.

---

## Feature 2: Search + Combined Filters

---

### Prompt S-1

**Prompt:**
> "Extend `GET /tasks` in the FastAPI backend to support text search via an optional `?q=` query parameter. The search must match the task title or description case-insensitively (OR between fields, AND with other filters). An empty or whitespace-only `q` must be ignored. Also add `?assignee=` as an exact string match filter. All filters combine with AND. Return 200 with an empty list when nothing matches. Do not add a new route. Do not change existing status or priority filter behavior."

**What AI returned:** Updated `get_all_tasks()` in `storage.py` with `q`, `tag`, and `assignee` parameters; updated `list_tasks()` in `main.py` to accept and pass through the new params.

**Accepted:** Full implementation — filter logic, parameter handling, AND combination.

**Edited:** Nothing needed editing for this prompt.

**Rejected:** AI initially returned a version that filtered `q` using Python's `re` module for regex support. Rejected — regex is unnecessary for a simple substring check and adds complexity. Replaced with `.lower() in .lower()` string check.

---

### Prompt S-2

**Prompt:**
> "Add a filter bar to `frontend/index.html` between the header and the board. Include: a search input (id=filter-q), a status select (id=filter-status, options: All/ToDo/InProgress/Done), a priority select (id=filter-priority, options: All/High/Medium/Low), a tag text input (id=filter-tag), and a Clear button (id=btn-clear-filters). Use a 300 ms debounce on the text inputs. On any filter change, rebuild the fetch URL from a `currentFilters` object and call `fetchTasks()`. `fetchTasks()` must read `currentFilters` and append query params. The Clear button must reset all controls and reload. Do not break the existing loading/error/empty states or drag-and-drop."

**What AI returned:** Filter bar HTML, CSS for `.filter-bar`, `currentFilters` object, `buildQueryString()`, `onFilterChange()`, `onSearchInput()` with debounce, updated `fetchTasks()`, Clear button handler.

**Accepted:** Full implementation.

**Edited:** Increased filter bar input `min-width` from 160px to 200px for the search field — it was too narrow on a standard-width window.

**Rejected:** AI suggested live search (no debounce) as the simpler option. Rejected — a 300 ms debounce prevents a request on every keystroke, which matters when users type more than one character.

---

### Prompt S-3 (Tests)

**Prompt:**
> "Write pytest tests for the new search and tag filter behavior on `GET /tasks`. Use the existing TestClient + fixture pattern from `tests/test_tasks.py`. Cover: search by title, search by description, case-insensitive search, no-match returns 200 with empty list, combined search + status filter, combined tag + priority filter. Each test must arrange data via POST /tasks, act with one GET /tasks, and assert the status code and relevant response body fields. Do not add imports unless missing."

**What AI returned:** 6 new search/filter tests appended to the existing test file.

**Accepted:** All 6 tests — they are well-named, isolated, and cover the specified scenarios.

**Edited:** Nothing edited.

**Rejected:** AI included a test for `?assignee=` filtering. Removed it — the assignee filter was added to the backend but is not surfaced in the frontend UI yet, so it does not need a test in this phase.
