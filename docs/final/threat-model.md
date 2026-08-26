# Threat Model — Task Tracker API

**Framework:** STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)  
**Scope:** API server + frontend, local development deployment

---

## System Overview

```
Browser (frontend/index.html)
    │  fetch()  HTTP/1.1
    ▼
FastAPI (app/main.py) :8000
    │
    ▼
In-memory dict (_tasks)
```

Trust boundary: the browser is an untrusted client. The API server is the only enforcement point.

---

## Threats

### T1 — Spoofing: Unauthenticated writes (STRIDE: S)

**Description:** Any client can POST, PATCH, or DELETE tasks without proving identity. There is no way to distinguish a legitimate user from an attacker.

**Likelihood:** High (no auth at all)  
**Impact:** Low (data is in-memory; no persistent damage; local-only deployment)  
**Mitigation:** Acceptable for local dev. For production: add API key or JWT auth.

---

### T2 — Tampering: Arbitrary task modification (STRIDE: T)

**Description:** A client that knows a task ID can change its title, description, priority, assignee, or tags without restriction.

**Likelihood:** High  
**Impact:** Low (same reasoning as T1)  
**Mitigation:** None needed at current scope. Status transitions are validated (`business_rules.py`), which is the only server-enforced business rule.

---

### T3 — Repudiation: No audit log (STRIDE: R)

**Description:** There is no log of who created or modified a task. `created_at` and `updated_at` timestamps are stored but the actor is not.

**Likelihood:** N/A  
**Impact:** Low  
**Mitigation:** For a production system, log the authenticated user on every write. Out of scope here.

---

### T4 — Information Disclosure: All tasks visible to all clients (STRIDE: I)

**Description:** `GET /tasks` returns all tasks to any caller. There is no concept of private tasks or per-user visibility.

**Likelihood:** High  
**Impact:** Low (local dev; no sensitive data in tasks)  
**Mitigation:** Acceptable. A production system would filter tasks by the authenticated user's identity.

---

### T5 — Denial of Service: Large payload / high request rate (STRIDE: D)

**Description:** No rate limiting and no maximum request body size beyond what FastAPI defaults enforce. A client can send many large requests.

**Likelihood:** Low (local dev; no public exposure)  
**Impact:** Low (process restart clears the problem)  
**Mitigation:** Add `slowapi` rate limiting and a `description` field length cap for public deployment.

---

### T6 — Denial of Service: Memory exhaustion via task creation (STRIDE: D)

**Description:** The in-memory store grows without bound. A client that creates millions of tasks will exhaust the server's memory.

**Likelihood:** Low  
**Impact:** Medium (process crash)  
**Mitigation:** A production system would use a database with server-side pagination. For local dev: acceptable.

---

### T7 — Elevation of Privilege: Not applicable (STRIDE: E)

**Description:** There are no privilege levels. All callers have the same (full) access.

**Likelihood:** N/A  
**Impact:** N/A  
**Mitigation:** N/A at current scope.

---

### T8 — XSS via task content reflected in frontend (STRIDE: T/I)

**Description:** If task fields (title, description, tags) were rendered via `innerHTML` without escaping, a stored XSS payload could execute in any viewer's browser.

**Likelihood:** Low — mitigation is in place  
**Impact:** High if unmitigated  
**Mitigation:** The `escape()` function in `frontend/index.html` HTML-encodes all task content before rendering. Verified in security review (SEC-007). Status: **mitigated**.

---

## Residual Risk Summary

| Threat | Residual Risk | Acceptable for Project Scope? |
|--------|--------------|-------------------------------|
| T1 Spoofing | High | Yes — local dev only |
| T2 Tampering | High | Yes — local dev only |
| T3 Repudiation | Medium | Yes — no auth system |
| T4 Info Disclosure | High | Yes — no sensitive data |
| T5 DoS (rate) | Low | Yes — not public |
| T6 DoS (memory) | Low | Yes — in-memory by design |
| T7 EoP | N/A | N/A |
| T8 XSS | Mitigated | Yes — escape() in place |

All residual risks are acceptable for a local development and learning project. The one active mitigation (XSS escaping) is verified and tested.
