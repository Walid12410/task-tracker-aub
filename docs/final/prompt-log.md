# Prompt Log — Final Project

This file records the prompts submitted to AI tools during the final project hardening phase, the tool used, and what was done with the output.

---

## Entry 1 — Dockerfile

**Tool:** Claude Code  
**Prompt:** "Write a minimal production-ready Dockerfile for a FastAPI app using Python 3.11-slim. The app is started with uvicorn app.main:app on port 8000. No database. No multi-stage build needed."

**Output summary:** Single-stage Dockerfile with `WORKDIR /app`, `COPY requirements.txt` first for layer caching, `pip install --no-cache-dir`, then `COPY app/ app/`, `EXPOSE 8000`, `CMD uvicorn`.

**Review:** Checked that `.env` was not copied into the image. The first draft included `COPY .env.example .env` which would bake a config file into the image. Removed that line. Verified with `docker build` locally.

**Decision:** Accepted with modification.

---

## Entry 2 — docker-compose.yml

**Tool:** Claude Code  
**Prompt:** "Write a docker-compose.yml that starts the FastAPI backend and serves the frontend directory via nginx on port 5500. Add a health check on the API before starting nginx."

**Output summary:** Two-service compose file: `api` (build `.`) and `frontend` (nginx:alpine with bind mount). Health check uses `urllib.request` instead of `curl` to avoid needing curl in the slim image.

**Review:** Verified the `depends_on: condition: service_healthy` chain so nginx waits. Confirmed the volume mount is `./frontend:/usr/share/nginx/html:ro`.

**Decision:** Accepted.

---

## Entry 3 — GitHub Actions CI

**Tool:** Claude Code  
**Prompt:** "Write a GitHub Actions workflow that: (1) installs Python 3.11, (2) runs pytest tests/ -v, and if tests pass, (3) builds the Docker image and smoke-tests GET /health."

**Output summary:** Two-job workflow with `needs: test` on the docker job. Smoke test starts the container, sleeps 5s, then `curl --fail http://localhost:8000/health`.

**Review:** Verified that the `needs:` dependency is set correctly. Checked that the sleep is long enough for uvicorn to start (5s is conservative). Confirmed the curl failure mode (`--fail` returns non-zero on HTTP 4xx/5xx).

**Decision:** Accepted.

---

## Entry 4 — Security review

**Tool:** Claude Code  
**Prompt:** "Review app/main.py, app/models.py, app/storage.py, Dockerfile, docker-compose.yml, and frontend/index.html for: OWASP Top 10 issues, secret leakage, CORS misconfiguration, XSS, injection, and any other risks. Report findings with severity."

**Output summary:** Seven findings. CORS hard-coded (Low), no auth (Medium), in-memory storage (Low), no rate limiting (Low), description no length cap (Low), no secrets in repo (Pass), XSS escape in place (Pass).

**Review:** Agreed with all findings. Confirmed XSS mitigation by reading the `escape()` function in `index.html`. Confirmed no secrets by re-reading `.gitignore`, `.env.example`, and `Dockerfile`.

**Decision:** Accepted. Written up in `docs/final/security-review.md`.

---

## Entry 5 — Threat model

**Tool:** Claude Code  
**Prompt:** "Write a STRIDE threat model for this FastAPI app + vanilla JS frontend. System: browser → FastAPI on :8000 → in-memory dict. Local deployment, no auth. Cover each STRIDE category with likelihood, impact, and mitigation status."

**Output summary:** Eight threats. T8 (XSS) is mitigated; T1–T6 are residual risks accepted for local dev scope.

**Review:** Checked each threat against the actual code. T8 verified by reading `escape()`. T5/T6 confirmed no rate limiting or pagination in storage.py.

**Decision:** Accepted. Written up in `docs/final/threat-model.md`.

---

## Entry 6 — AGENTS.md

**Tool:** Claude Code  
**Prompt:** "Write an AGENTS.md file that documents all AI tools used in this project, the prompts submitted, the output received, what was reviewed, and what was accepted or rejected. Include mid-course AI use (Cursor, ChatGPT, Claude) and final-project use."

**Output summary:** Full governance document covering 6 tools/interactions with accept/reject decisions.

**Review:** Verified all entries are accurate against the actual codebase. Confirmed the rejected regex search is correctly described (it used `re.search`, not `re.compile`). Confirmed the `validate_tags` description matches the actual code in `models.py`.

**Decision:** Accepted.

---

## Entry 7 — Architecture Decision Records

**Tool:** Claude Code  
**Prompt:** "Write ADRs for: in-memory storage, Pydantic v2, status transition enforcement in business_rules.py, CORS hard-coding, Docker single-stage, and pytest with TestClient."

**Output summary:** Six ADRs covering every major architectural decision in the project.

**Review:** Cross-checked each ADR against the actual code to confirm the described rationale matches reality. ADR-003 (business rules) correctly names `VALID_TRANSITIONS` and `validate_status_transition`.

**Decision:** Accepted.

---

## Entry 8 — README.md

**Tool:** Claude Code  
**Prompt:** "Rewrite README.md to include: project overview, directory structure, Docker quick start, local quick start, environment variables table, API reference (routes, filter params, task object shape, status transitions), test instructions, CI description, known limitations."

**Output summary:** Full README covering all required sections.

**Review:** Verified all API paths, parameter names, and field names against the actual code. Confirmed the status transition table matches `VALID_TRANSITIONS` in `business_rules.py`.

**Decision:** Accepted.
