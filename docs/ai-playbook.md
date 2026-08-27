# AI Playbook — Task Tracker API

This document defines my personal rules for when and how I use AI tools, how I review their output, and what I am still working out. It applies to this project and any future project where I use AI assistance.

---

## When I reach for AI first

I use AI as the first tool in these situations:

- **Scaffolding and boilerplate.** Dockerfiles, CI workflow files, `.gitignore`, `docker-compose.yml` — files with a well-known correct shape that I would otherwise copy from documentation.
- **First-draft code for a clearly specified requirement.** When I can write the requirement as a precise prompt (file names, function signatures, constraints), AI produces a useful starting point faster than writing from scratch.
- **Code review and security review passes.** AI can scan multiple files simultaneously and flag patterns I might not be looking for. I treat the output as a checklist hypothesis, not a verdict.
- **Test-case generation.** After I write the feature code, AI is good at listing boundary conditions I might have missed. I verify and add only the cases that actually test real behavior.
- **Documentation.** Structured documents (README sections, ADR templates, release notes) where the facts are mine and the format is standard.

In this project, AI contributed to the Dockerfile, CI config, docker-compose, validators, and the security review. All went through the prompt → read → test → decide loop before being committed.

---

## When I do not

I do not reach for AI first in these situations:

- **Security-critical logic.** Authentication checks, authorization rules, input sanitization, and secret handling require manual design and manual verification. AI can review this code after I write it, but it does not write it.
- **When I have not understood the requirement myself.** Prompting AI before I can state the requirement clearly produces output I cannot evaluate. I write the requirement in plain language first; if I cannot do that, I am not ready to prompt.
- **When I cannot explain the output.** If AI produces code I cannot read and explain line by line, I do not commit it. I either research it until I own it or rewrite it. The rejected regex search in `docs/final-ai-review.md` section 4 is the example from this project.
- **Secrets, credentials, and tokens.** AI tools must not generate secret keys, passwords, or any value that would be a credential. Placeholders (`SECRET_KEY = "changeme"`) are removed before committing.
- **Final architectural decisions.** AI can propose options. I make the decision and document it in the ADR.

---

## My non-negotiables

These rules are not guidelines — they are hard constraints that apply to every AI interaction.

**N-01: Read every line before committing.**
No AI-generated output is committed without being read in full by me. "It ran" is not a review. This caught a hallucinated control-flow description (CR-03) and a SQL injection finding on a project with no database (SEC-08).

**N-02: Run the full test suite after every AI-assisted change.**
`pytest tests/ -v` must pass before any AI-generated code is committed. A passing test suite is a necessary condition, not a sufficient one.

**N-03: No AI-authored secrets or credentials.**
Any AI output that includes a placeholder credential is edited to remove it before committing. The `.gitignore` excludes `.env`. The Dockerfile does not `COPY .env`. These exist because secrets in git history are hard to expunge.

**N-04: Reject and rewrite if I cannot explain the dependency.**
If AI output adds an import or pattern I cannot explain from memory, I either research it fully or rewrite without it. Owning every line means being able to explain every line.

**N-05: Document every non-trivial accept or reject.**
Any AI output that is modified, rejected, or accepted with a rationale must be documented in `AGENTS.md` or `docs/final-ai-review.md`. Silent accepts of uncritical boilerplate (standard `.gitignore` entries, comment headers) do not need to be logged.

**N-06: No AI output for security-critical logic without manual verification.**
Any code that enforces a security boundary must be manually verified against intended behavior even if AI generated it. The XSS protection was verified by typing `<script>alert(1)</script>` into the live UI, not just by reading the AI's analysis.

---

## My review rules

Every AI interaction in this project followed a four-step loop:

1. **Prompt** — state the goal precisely. Include file names, function names, and constraints. Vague prompts produce vague output.
2. **Read** — read every line of the output before doing anything with it. Look for imports, side effects, and incorrect assumptions about the codebase.
3. **Test** — run the relevant verification (pytest, docker build, curl, manual UI test). Do not commit until the verification passes.
4. **Decide** — accept verbatim, accept with modification, or reject entirely. Log the decision if it is non-trivial.

For AI review findings specifically (code review, security review), I grade each finding before acting:

| Grade | Meaning |
|-------|---------|
| **Valid / A** | Finding is correct and verified. Act on it. |
| **Valid / B** | Finding is correct but low priority. Log for backlog. |
| **Partially valid / C** | Finding is real but overstated or low value. Note and move on. |
| **Invalid / D** | Finding is wrong. Verify by reading the file. Do not act. |

This grading approach is documented in full in `docs/final-ai-review.md`.

---

## What I am still figuring out

- **How to write prompts that reduce hallucinations.** CR-03 (wrong control flow) and SEC-08 (SQL injection on an in-memory dict) both came from the same review pass. I do not yet have a reliable way to prompt that prevents this class of error — the only defense I have is reading every finding before acting.

- **When AI code review adds real value vs. noise.** In this project, 6 of 8 security findings were valid and 4 of 5 code findings were valid or partially valid. That is useful but not reliable enough to trust without verification. I am not sure whether better prompts, a different tool, or more context in the prompt would improve that ratio.

- **How to handle AI suggestions for refactors I did not ask for.** Several AI outputs included unsolicited refactoring suggestions alongside the requested change. I accepted none of them — but I am not sure whether that is the right instinct or whether I am leaving real improvements on the table.

- **Where the line is between "AI-assisted" and "AI-authored."** Most files in this project are somewhere in between. I reviewed and modified every file, but some (Dockerfile, CI config) I accepted nearly verbatim. I am not confident I have the right mental model for describing authorship honestly.

---

## Decision Card

Quick reference for deciding how to handle an AI interaction.

| Situation | Action |
|-----------|--------|
| Boilerplate with a known correct shape | Prompt AI, read output, commit after tests pass |
| First-draft feature code | Prompt AI, read every line, run tests, decide |
| Security-critical logic | Write manually, use AI only for review pass afterward |
| AI review finding — plausible | Verify by reading the relevant file before acting |
| AI review finding — surprising | Verify by reading the file; default to skepticism |
| AI output contains something I cannot explain | Research fully or rewrite without it |
| AI output contains a credential placeholder | Remove before committing, no exceptions |
| AI proposes an unsolicited refactor | Do not commit; log if the idea has merit |
| Requirement is unclear to me | Write the requirement in plain language first; do not prompt until I can |
