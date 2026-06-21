# Sprint 29 — CI/CD Pipeline Hardening

## Goal
Protect `main` from unguarded pushes, add a CI gate that runs before every merge, and clean up dead branches. Minimum safe posture for a live client system.

---

## PIPE-3 — Dead Branch Cleanup · P0

**As the developer,**
**I want stale merged branches removed from the remote,**
**So that the repo only shows branches that represent active work.**

### Acceptance Criteria
- `dev` deleted from remote and local
- `feat/sprint-7-public-holidays-rate-codes-workspace-config-reconciliation-resolution` deleted from remote and local
- `feature/sequential-executor-pension-nhf-fix` deleted from remote and local
- `git branch -r` shows only `origin/main` and `origin/uat`
- All three confirmed fully merged into `main` before deletion

### Out of Scope
- Auto-delete on merge (low value at this repo volume)

---

## PIPE-2 — GitHub Actions CI · P1

**As the developer,**
**I want a CI check to run on every push to `uat` and every PR targeting `main`,**
**So that I know both the frontend builds cleanly and the backend tests pass before anything reaches production.**

### Acceptance Criteria
- `.github/workflows/ci.yml` created
- Triggers: push to `uat`, pull_request targeting `main`
- **Frontend job:** `npm ci && npm run build` (type check included via `tsc -b && vite build`)
- **Backend job:** `pip install -r requirements.txt` then `python -m pytest tests/ -x -q` (pure Python, no DB)
- Both jobs run in parallel
- CI status visible on GitHub commit / PR
- Failing CI blocks merge to `main` (enforced by PIPE-1)

### Out of Scope
- Database-backed integration tests (deferred to test harness sprint)
- Render deploy hooks
- Slack/email notifications

---

## PIPE-1 — Branch Protection on `main` · P1

**As the developer,**
**I want `main` to be protected from direct and force pushes,**
**So that production can only be updated via a merge that has passed CI.**

### Acceptance Criteria
- Direct push to `main` rejected by GitHub
- Force-push to `main` blocked
- Merge to `main` requires both `frontend` and `backend` CI checks to pass
- `enforce_admins: false` (allows emergency bypass for solo dev if CI has a config error)
- Confirmed: direct push attempt after setup is rejected

### Out of Scope
- Required PR reviewer (solo developer — no second reviewer)
- PR template

### Dependency
PIPE-1 must be set up **after** PIPE-2 CI is confirmed passing — otherwise `main` becomes unmerge-able if CI has a config error.

---

## Execution Order
1. PIPE-3 — delete branches (no risk, 5 mins)
2. PIPE-2 — create CI workflow, push to `uat`, verify green
3. PIPE-1 — enable branch protection (only after CI is green)
