# User Stories — Mid-Course Project

## Feature 1: Tags / Labels

---

**US-T1** — Add tags when creating a task

> As a team member, I want to attach one or more tags when I create a task so that I can categorize work by topic or component.

Acceptance criteria:
- The New Task modal includes a Tags field accepting comma-separated values.
- Each tag is trimmed; blank tags are rejected with a 422 before saving.
- The created task is returned with a `tags` array in the API response.
- A task with no tags defaults to an empty list — no error.

**AI assumption I reviewed and corrected:**
The AI initially proposed storing tags as a single comma-separated string in the model. I corrected this to `list[str]` in Pydantic so validation runs per-tag and the API returns a proper array. The string approach would have made filtering and validation more fragile.

---

**US-T2** — See tag chips on task cards

> As a team member, I want to see a task's tags displayed as chips on its card so that I can understand the context of a task at a glance without opening it.

Acceptance criteria:
- Cards with one or more tags show a row of colored chips below the description.
- Cards with no tags show no chip row — no empty space wasted.
- Chips are read-only; editing tags requires opening the Edit modal.

---

**US-T3** — Edit tags on an existing task

> As a team member, I want to edit a task's tags without affecting its other fields so that I can reclassify work as priorities change.

Acceptance criteria:
- The Edit modal pre-fills the Tags field with the task's current tags joined by ", ".
- Saving with a different tag list updates only the tags; title, status, priority, and assignee are unchanged.
- Saving with an empty Tags field clears all tags (`tags: []`).
- A whitespace-only tag entry is rejected with a visible error — the modal stays open.

**AI assumption I reviewed and corrected:**
The AI originally made `tags` required in `TaskUpdate`. I changed it to `Optional[list[str]] = None` so that a PATCH request without a `tags` key does not clear the existing tags. This matches how all other optional fields behave in the update model.

---

**US-T4** — Filter the board by tag

> As a team member, I want to type a tag name in the filter bar to see only tasks that carry that tag so that I can focus on one area of work.

Acceptance criteria:
- The filter bar includes a tag input field.
- Typing a tag name sends `?tag=<value>` to `GET /tasks`.
- Matching is case-insensitive exact match (e.g., "frontend" matches "Frontend").
- All three columns remain visible; columns with no matching tasks show the empty placeholder.
- Clearing the tag input restores all tasks.

---

**US-T5** — Invalid tags are rejected with a clear error

> As a developer, I want the API to reject invalid tag values with a 422 so that data stays clean without requiring me to guess what is allowed.

Acceptance criteria:
- An empty string tag (`""`) in the `tags` array returns 422.
- A whitespace-only tag (`"  "`) returns 422.
- More than 10 tags in one request returns 422.
- A tag exceeding 50 characters returns 422.
- Valid tags up to 10 items are accepted.

---

## Feature 2: Search + Combined Filters

---

**US-S1** — Search tasks by keyword

> As a team member, I want to type a keyword into a search box so that I can find relevant tasks without scrolling through every column.

Acceptance criteria:
- The filter bar includes a text search input.
- Typing triggers a debounced request to `GET /tasks?q=<term>` (300 ms delay).
- The search matches task title and description, case-insensitively.
- All three columns stay visible; columns with no matching tasks show the empty placeholder.
- Clearing the search input restores all tasks.

**AI assumption I reviewed and corrected:**
The AI initially proposed filtering on the frontend from the already-loaded task list. I rejected this because it is inconsistent with how status and priority filters work (those call the backend) and would break if pagination were added. I kept all filtering on the backend so one code path handles everything.

---

**US-S2** — Filter by status

> As a team member, I want to filter tasks by status so that I can focus only on in-progress work without other cards cluttering the board.

Acceptance criteria:
- A status dropdown in the filter bar offers: All Statuses, To Do, In Progress, Done.
- Selecting a value sends `?status=<value>` to the backend.
- Selecting "All Statuses" removes the status filter.
- Invalid status values sent directly to the API return 422 (existing behavior, unchanged).

---

**US-S3** — Filter by priority

> As a team member, I want to filter tasks by priority so that I can see only high-priority items during a triage session.

Acceptance criteria:
- A priority dropdown offers: All Priorities, High, Medium, Low.
- Selecting a value sends `?priority=<value>` to the backend.
- Priority sort order within each column is preserved after filtering.
- Selecting "All Priorities" removes the priority filter.

---

**US-S4** — Combine search and filters with AND behavior

> As a team member, I want to use a keyword search together with status and priority filters so that I can narrow results precisely.

Acceptance criteria:
- When search and at least one dropdown filter are active, the backend applies all conditions with AND logic.
- No matching tasks returns HTTP 200 with an empty list — not an error.
- All three columns remain visible with empty placeholders.

**AI assumption I reviewed and corrected:**
The AI suggested using OR logic between filters to maximize results. I corrected this to AND because users expect that adding more filters narrows the result, not broadens it. The backend implementation uses sequential filter application to achieve this.

---

**US-S5** — Clear all filters at once

> As a team member, I want a single Clear button that resets all filters simultaneously so that I can quickly return to the full board view.

Acceptance criteria:
- A Clear button appears in the filter bar.
- Clicking it resets the search input, both dropdowns, and the tag input to their default values.
- The board immediately reloads with all tasks and no active filters.
