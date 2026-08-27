# AI Playbook — Task Tracker API

This document defines the rules under which AI tools are permitted to contribute to this project, how outputs are reviewed before use, and who owns what in the final result.

---

## 1. AGENTS.md Guardrails

These rules apply to every AI tool used in this project (Claude Code, Cursor, ChatGPT, Claude web). They are binding for the current project and apply to any future contributor who uses AI tools on this codebase.

### G-01: Read every line before committing

No AI-generated output is committed to the repository without being read in full by the author. "It ran" is not a review. Reading every line is mandatory.

**Why:** The AI code review mini-log (`docs/final-ai-review.md`, section 1) contains an example where AI described the wrong control flow (CR-03). Without line-by-line reading, that incorrect description could have been taken as fact. The security review produced a SQL injection finding on a project with no database (SEC-08). These errors are only caught by reading.

### G-02: Run the tests after every AI-assisted change

After any AI-generated code is added to the project, the full test suite (`pytest tests/ -v`) must pass before the change is committed. A passing test suite is a necessary condition for committing AI output, not a sufficient one.

**Why:** Tests can catch regressions that code review misses. The tags validator (`validate_tags`) was verified by running `test_patch_task_tags_can_be_cleared` and `test_patch_unrelated_update_preserves_tags` specifically because the correct behavior was non-obvious.

### G-03: No AI-authored secrets or credentials

AI tools must not be asked to generate secret keys, tokens, passwords, or any value that would be a credential in production. Any AI output that happens to include a placeholder credential (e.g., `SECRET_KEY = "changeme"`) must be removed before committing.

**Why:** This project's `.gitignore` excludes `.env`. The `Dockerfile` does not `COPY .env`. These rules exist because secrets committed to a repository are hard to expunge fully (they remain in git history). AI tools do not know which placeholders are safe and which are not.

### G-04: Reject and rewrite if the output introduces unclear dependencies

If AI output adds an import, library, or pattern that the author cannot explain from memory, the output must be either explained fully before accepting or rewritten without that dependency.

**Why:** The rejected regex search (`docs/final-ai-review.md`, section 4) is the canonical example. `re.escape` + `re.compile` + `re.IGNORECASE` is technically correct but harder to reason about than `q_lower in text.lower()`. The simpler version was substituted. This rule is not about avoiding complexity — it is about ensuring the author owns every line.

### G-05: Document every non-trivial accept or reject

Any AI output that is modified, rejected, or accepted with a comment about why it was accepted must be documented in either `AGENTS.md` (for governance) or `docs/final-ai-review.md` (for the final review record). Silent accepts of uncritical boilerplate (e.g., `.gitignore`, standard headers) do not need to be logged.

**Why:** Provenance matters. A future reader should be able to determine whether any given file was AI-generated, human-written, or AI-generated and modified, and what the review decision was.

### G-06: No AI output for security-critical logic without manual verification

Any code that enforces a security boundary — authentication checks, authorization rules, input sanitization, secret handling — must be manually verified against the intended behavior even if AI generated it.

**Why:** Security code that looks correct can still be wrong in subtle ways. The XSS protection was verified manually by typing `<script>alert(1)</script>` into the UI (see `docs/final-ai-review.md`, section 3a), not just by reading the AI's analysis.

---

## 2. Workflow

Every AI interaction in this project followed this four-step loop:

1. **Prompt** — state the goal precisely. Include the file names, function names, and constraints. Vague prompts produce vague output.
2. **Read** — read every line of the output before doing anything with it. Look for imports, side effects, incorrect assumptions about the codebase.
3. **Test** — run the relevant verification (pytest, docker build, curl, manual UI test). Do not commit until the verification passes.
4. **Decide** — accept verbatim, accept with modification, or reject entirely. Log the decision if it is non-trivial.

This loop was applied to every AI interaction in this project, from the Pydantic validator to the Dockerfile to the security review.

---

## 3. Tool Inventory

| Tool | Role in this project | Phase |
|------|---------------------|-------|
| ChatGPT | Design sounding board — tags data model, filter logic | Mid-course |
| Cursor (inline chat) | Code generation — models, storage, routers | Mid-course |
| Claude (web) | Bulk code generation — validators, test cases | Mid-course |
| Claude Code (CLI) | Dockerfile, docker-compose, CI, docs, security review | Final project |

No tool was used to commit directly to the repository. All AI output passed through the prompt → read → test → decide loop.

---

## 4. What AI Is Not Permitted to Do on This Project

- Commit code directly (no autonomous commit hooks or agents).
- Generate or handle real credentials, API keys, or tokens.
- Modify the `.gitignore` or any security-boundary configuration without explicit review.
- Be treated as authoritative on codebase structure without verification — AI descriptions of the code are hypotheses until confirmed by reading the file.

---

## 5. Ownership Statement

Every file in this repository falls into one of three categories:

### 5a. Written by me, no AI involvement

- `app/models.py` — validators were generated by AI and then modified; the structure and field choices are mine.
- `app/storage.py` — the search filter logic was AI-generated, rejected, and rewritten by me (see `docs/final-ai-review.md`, section 4).
- `tests/test_tasks.py` — all test cases were reviewed and run locally. The test for tag preservation (`test_patch_unrelated_update_preserves_tags`) was written in response to a gap I caught in the AI's original model proposal.

### 5b. AI-generated and accepted verbatim after review

- `Dockerfile` — reviewed line by line; build verified locally.
- `.github/workflows/ci.yml` — reviewed; `needs: test` dependency verified.
- `docker-compose.yml` — reviewed; health check dependency verified.

### 5c. AI-generated and modified before committing

- `Dockerfile` (first draft) — removed `COPY .env.example .env` line that would have baked a config file into the image.
- `app/storage.py` search filter — regex implementation rejected; replaced with simple string containment.

I can explain any line in any file in this repository. The test suite passes. The Docker image builds and the health check passes inside the container. All AI interactions are logged in `AGENTS.md` and `docs/final-ai-review.md`.
