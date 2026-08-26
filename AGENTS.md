# AGENTS.md — AI Governance for Task Tracker API

This document records every AI tool used across the lifecycle of this project, the role each tool played, how outputs were reviewed, and what was accepted or rejected. It satisfies the AI governance requirement of the final-project checkpoint.

---

## Tools Used

| Tool | Role |
|------|------|
| **Claude Code (CLI)** | Final-project hardening: Docker, CI, security review, docs |
| **Cursor (inline chat)** | Primary coding assistant during mid-course — model/storage layers |
| **ChatGPT** | Design sounding board — tags data model, filter logic planning |
| **Claude (web)** | Bulk code generation (test cases, documentation structure) |

---

## Prompts and Outcomes

### 1. Tags data model — ChatGPT (mid-course)

**Prompt (paraphrased):** "Should tags be stored as a comma-separated string or a list of strings in the Pydantic model?"

**Output:** Recommended `list[str]` with a field validator, arguing it avoids parsing bugs and works natively with JSON.

**Review:** Agreed with the recommendation. Compared to storing as a single string and splitting — the validator approach is safer because Pydantic validates each element individually.

**Decision:** Accepted. Implemented as `tags: list[str] = []` in `TaskCreate`.

---

### 2. `validate_tags` field validator — Claude (web, mid-course)

**Prompt (paraphrased):** "Write a Pydantic v2 field validator for `tags: list[str]` that rejects empty strings, trims whitespace, limits count to 10, and limits each tag to 50 chars. Also write the `Optional[list[str]]` version for `TaskUpdate` where `None` means no change and `[]` means clear."

**Output:** Complete `validate_tags` for both `TaskCreate` and `TaskUpdate` in one pass.

**Review:** Read every line carefully. The `None` guard in `TaskUpdate` (`if v is None: return v`) was correct and non-obvious — without it, `None` would have been iterated and raised an error.

**Decision:** Accepted verbatim. Verified with `test_patch_task_tags_can_be_cleared` and `test_patch_unrelated_update_preserves_tags`.

---

### 3. Search filter implementation — Claude (web, mid-course)

**Prompt (paraphrased):** "Add a `q` parameter to `get_all_tasks` that filters by case-insensitive substring match across title and description."

**Output:** Used `re.search(re.escape(q), text, re.IGNORECASE)` — technically correct but unnecessarily complex.

**Review:** Caught the regex approach. A plain `q_lower in title.lower()` check is simpler, has no import, and cannot throw `re.error` if the user types `(` or `*`.

**Decision:** Rejected. Rewrote with simple string containment. This is documented in `docs/midcourse/reflection.md`.

---

### 4. Dockerfile — Claude Code (final project)

**Prompt:** "Write a minimal production-ready Dockerfile for this FastAPI app using Python 3.11-slim."

**Output:** Multi-stage was not needed; single-stage with `--no-cache-dir` is sufficient for this project size.

**Review:** Verified the WORKDIR, COPY order (requirements first for layer caching), and that no `.env` files are baked in.

**Decision:** Accepted with one change — removed the `.env.example → .env` copy that was in the first draft; environment should be injected at runtime.

---

### 5. GitHub Actions CI — Claude Code (final project)

**Prompt:** "Write a GitHub Actions workflow that installs Python 3.11, runs pytest, then builds and smoke-tests the Docker image."

**Output:** Two-job workflow (`test` → `docker`) with a curl health-check smoke test.

**Review:** Checked that the `needs: test` dependency is correct so Docker does not build on a failing test suite. Verified the smoke-test sleep is long enough for uvicorn startup.

**Decision:** Accepted.

---

### 6. Security review — Claude Code (final project)

**Prompt:** "Review the FastAPI app for OWASP Top 10 issues, secret leakage, injection risks, and CORS misconfiguration."

**Output:** Identified hard-coded CORS origin, in-memory storage not suitable for multi-process deployment, no rate limiting, and no input length enforcement on `description`.

**Review:** Assessed each finding against project scope (learning project, single process). Hard-coded CORS is a real issue noted in the ADR. Description length is not enforced — added to known limitations.

**Decision:** CORS finding documented in `docs/final/security-review.md`. Other findings accepted as known limitations rather than blocking issues at this scale.

---

## What Was Never Accepted Without Review

- No AI output was committed without reading every line.
- All test cases were run locally before commit.
- Regex-based search was rejected and rewritten (see item 3 above).
- No secrets, tokens, or credentials appear in any AI-generated file.

---

## Governance Rules Applied to This Project

1. **Read before commit** — every AI output was read in full before being added to the codebase.
2. **Run the tests** — after every AI-assisted change, the test suite was run to confirm no regression.
3. **No AI-authored secrets** — `.env` files are excluded from version control; Docker does not bake them in.
4. **Reject if unclear** — when AI output introduced unfamiliar patterns (e.g., regex for search), it was replaced with the simplest correct alternative.
5. **Document the decision** — every non-trivial accept or reject is recorded here or in `docs/midcourse/reflection.md`.
