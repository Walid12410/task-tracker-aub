# Reflection — Final Project

## What this phase added

The final project hardening phase added four things that were absent from the mid-course submission:

1. **Containerization** — `Dockerfile` and `docker-compose.yml` let anyone run the full stack with `docker compose up` without configuring Python locally.
2. **CI** — `.github/workflows/ci.yml` runs the test suite and builds the Docker image on every push, catching regressions before they reach the main branch.
3. **Security and threat documentation** — `docs/final/security-review.md` and `docs/final/threat-model.md` make the risk profile explicit rather than implicit.
4. **AI governance** — `AGENTS.md` and this prompt log document every AI interaction so the project's provenance is transparent.

No new product features were added. The goal was to make the existing code maintainable by a teammate who had not worked on it before.

## How AI was used in this phase

All final-project work was done with Claude Code (the CLI tool). The workflow was:

1. Describe the goal precisely in the prompt.
2. Read every line of the output before doing anything with it.
3. Verify by running the relevant tool (docker build, pytest, curl).
4. Accept, modify, or reject.

The one modification made to AI output was removing `COPY .env.example .env` from the first draft of the Dockerfile. That line would have baked a config file into the image, which is not wrong for this project (the file has no secrets) but sets a bad pattern. The corrected version injects environment variables at runtime via `docker-compose.yml`.

## What I own in the result

Every file in this submission was either:
- Written by me (mid-course: `app/models.py` validators, `app/storage.py` search logic, all test cases after verification), or
- Written by AI and reviewed line-by-line before committing (final-project: Dockerfile, CI, docs), or
- Written by AI and modified before committing (Dockerfile: removed baked-in config).

I can explain any line in any file. The test suite passes. The Docker image builds and the health check passes inside the container.

## What I would do differently

If I were to start over, I would enforce the `description` length limit from the beginning (it is currently unbounded on the server). The mid-course reflection noted that AI's first search implementation used `re` unnecessarily — that catch reinforced the habit of reading output carefully rather than trusting it because it runs.

The most durable skill from this course is the prompt → read → test → accept/reject loop. AI tools produce plausible output, not necessarily correct output. The review step is where the engineer's judgment matters.
