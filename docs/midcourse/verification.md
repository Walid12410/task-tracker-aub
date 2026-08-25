# Verification — Mid-Course Project

## Baseline (before any changes)

Command run:
```bash
venv/bin/pytest tests/test_tasks.py -v
```
Result: **23 passed, 0 failed**

Branch: `mid-course-project` (already existed, clean working tree)

---

## After feature implementation

Command run:
```bash
venv/bin/pytest tests/test_tasks.py -v
```
Result: **40 passed, 0 failed**

New tests added: 17 (11 tags, 6 search/filter)

---

## How to run

```bash
# Backend
cd "/Users/macuser/Desktop/aub course/task-tracker-api"
venv/bin/uvicorn app.main:app --reload --port 8000

# Frontend (must be served over HTTP, not file://)
cd frontend
python3 -m http.server 5500
# Open: http://localhost:5500

# Tests
venv/bin/pytest tests/test_tasks.py -v
```

---

## Manual browser checks

- Board loads with 7 seeded tasks; tag chips visible on each card.
- Filter bar: typing "backend" in search narrows cards; clearing restores all.
- Tag filter: typing "docs" shows only the documentation task.
- Status + priority dropdowns filter the board; columns stay visible even when empty.
- Clear button resets all filters and restores the full board.
- New Task modal includes Tags field; entering "api, v2" creates chips on the card.
- Edit modal pre-fills tags correctly; saving updates chips on the card.

---

## Break Test evidence

**Break Test 1 — tag validation**

Temporarily changed the assertion in `test_create_task_with_empty_string_tag_returns_422` to expect `200` instead of `422`.

Result: `FAILED — assert 422 == 200`. Test correctly catches the validation.

Reverted immediately.

**Break Test 2 — search filter**

Temporarily removed the `q` filter branch from `storage.get_all_tasks()` (commented out the `if q is not None` block).

Result: `test_list_tasks_search_by_title_returns_matching FAILED — AssertionError: assert 2 == 1`. The test correctly detects that filtering is not applied.

Reverted immediately.

---

## Pre-existing issues (unchanged)

| Item | Detail |
|---|---|
| `app/routers/tasks.py` | Still a stub — all routes remain in `main.py` |
| `app/service.py` | All methods raise `NotImplementedError` — unused |
| `app/repository.py` | All methods raise `NotImplementedError` — unused |
| In-memory only | Data resets on server restart |
