# Stage 10 Evidence: CI and Test-Harness State

All reads performed 2026-07-17 at git commit `e4ad484` (branch `uat`, clean tree). Transient query outputs duplicated here per `_core/EVIDENCE-STANDARD.md` (they change as the repo evolves).

## 1. CI workflow shape — `.github/workflows/tests.yml` (full-file read)

Two jobs only:

1. **`backend`** — "Backend suite (fresh DB from migrations)": Postgres 16 service container, `python -m alembic upgrade head` against the fresh database, then `python -m pytest -q`. Env: `DATABASE_URL` → the service container, `ENVIRONMENT: test`.
2. **`frontend-typecheck`** — `npm ci` + `npx tsc --noEmit` in `frontend/`. **No frontend test execution — typecheck only.**

Triggers (lines 3–7): `push` and `pull_request` on `uat`/`main` **only**. There is **no `schedule:` trigger and no `workflow_dispatch:`** — the workflow has no seam today for scheduled (cron) assurance jobs; one must be added when the first scheduled control lands.

```
grep -c "schedule" .github/workflows/tests.yml   → 0
```

## 2. Frontend test harness — absent

- `frontend/package.json` `scripts`: `dev`, `build`, `lint`, `preview` — **no `test` script**.
- `devDependencies` contain no test framework or testing library (no vitest/jest/@testing-library/*; full list read: eslint toolchain, tailwind, typescript, vite, React types only).
- No `vitest.config.*` or `jest.config.*` exists in `frontend/`.
- Zero test files: `find frontend/src -name "*.test.*" -o -name "*.spec.*" | wc -l` → **0**.

Corroborating documented intent: `docs/test-reports/test-harness/test-harness-checklist.md` §4 parks **T4.5** ("`grade_code` null on bulk upload") with the reason *"frontend-only rule, no frontend harness exists; separate decision with Michael"* — the absence is known and previously deliberate, not an oversight discovered here.

## 3. Backend suite state (direct observed behaviour, this session)

```
python -m pytest --collect-only -q   → 328 tests collected in 0.98s
python -m pytest -q                  → 327 passed, 1 skipped, 48 warnings in 6.93s
```

Run against the local dev DB (the standing rule notes CI's fresh migrated DB is the arbiter; this run is corroboration that the suite is currently green, not the authority). The documented count in `CLAUDE.md` ("306 passed, 1 intentional Phase-2 skip", dated 2026-07-12) is stale by 21 tests — the suite has grown since the harness workstream closed; the enforcement machinery (pre-push hook + CI) is unchanged.

## 4. Existing conventions the assurance design builds on (documented + verified)

- Fresh-DB rule: CI builds the schema with `alembic upgrade head` per §1 — confirmed in the workflow file, not just in `CLAUDE.md`.
- Pre-push gate: `.githooks/pre-push` runs pytest + `tsc --noEmit` (`core.hooksPath` set) — per `CLAUDE.md` Test Harness section and checklist §5 (verified-live note of 2026-07-12); not re-executed this session.
- Standing rule: every bug fix ships with a regression test named for the invariant it protects (`CLAUDE.md`; checklist §6).
