# Deployment Guide — Render (backend) + Vercel (frontend)

This guide deploys the payroll platform for UAT client access using free-tier hosting.
Total setup time: ~20 minutes.

---

## Prerequisites

- [ ] Render account — [render.com](https://render.com) (free)
- [ ] Vercel account — [vercel.com](https://vercel.com) (free)
- [ ] GitHub repo already pushed (the `render.yaml` and `vercel.json` files are in the repo root)

---

## Step 1 — Deploy backend on Render

Render reads `render.yaml` from the repo root and automatically provisions the database and backend service.

1. Go to [render.com](https://render.com) → **New** → **Blueprint**
2. Connect your GitHub account and select the `agentic-payroll-platform` repository
3. Render will detect `render.yaml` and show two resources to create:
   - `payroll-db` (free PostgreSQL)
   - `payroll-backend` (free web service, Docker)
4. Click **Apply** — Render will start building the Docker image

### Set required environment variables

After the first deploy completes, go to **payroll-backend → Environment** and set these values:

| Variable | How to generate |
|----------|----------------|
| `SECRET_KEY` | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ENCRYPTION_KEY` | `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `ALLOWED_ORIGINS` | Leave blank for now; update after Step 2 with your Vercel URL |

`DATABASE_URL` is **auto-injected** by Render from the managed database — do not set it manually.

5. After setting the env vars, trigger a **Manual Deploy** so the service restarts with the new values
6. The start command (`alembic upgrade head && uvicorn ...`) runs migrations automatically on every deploy
7. Note your backend URL — it will look like:
   ```
   https://payroll-backend.onrender.com
   ```

### Verify backend health

```
curl https://payroll-backend.onrender.com/api/v1/health
```

Expected response: `{"status": "ok"}` (or similar — depends on your health route).

---

## Step 2 — Deploy frontend on Vercel

1. Go to [vercel.com](https://vercel.com) → **New Project** → **Import from GitHub**
2. Select the `agentic-payroll-platform` repository
3. **Recommended:** Set **Root Directory** to `frontend`
   - Framework Preset: Vite (auto-detected)
   - Build Command: `npm run build` (default)
   - Output Directory: `dist` (default for Vite)
   - Vercel will use `frontend/vercel.json` for the SPA rewrite rules
4. **Alternative:** Leave Root Directory as repo root
   - The root-level `vercel.json` will configure the build to run from `frontend/`
   - Build Command: `cd frontend && npm ci && npm run build`
   - Output Directory: `frontend/dist`
4. Under **Environment Variables**, add:

   | Name | Value |
   |------|-------|
   | `VITE_API_URL` | `https://payroll-backend.onrender.com` ← your Render URL from Step 1 |

5. Click **Deploy**

Vercel will build the frontend and assign a URL like `https://payroll-xyz.vercel.app`.

---

## Step 3 — Tighten CORS (recommended)

After Step 2, go back to Render → **payroll-backend → Environment** and update:

```
ALLOWED_ORIGINS=https://payroll-xyz.vercel.app
```

If you have a custom domain, add it too (comma-separated):
```
ALLOWED_ORIGINS=https://payroll-xyz.vercel.app,https://payroll.yourcompany.com
```

Trigger another manual deploy on Render after this change.

---

## Step 4 — Post-deploy checklist

- [ ] Visit the Vercel URL → app loads without console errors
- [ ] Login / workspace creation works
- [ ] Health endpoint responds: `GET /api/v1/health` returns 200
- [ ] Run a test payroll to confirm DB writes are working
- [ ] Check Render logs for any migration errors on first deploy

---

## Updating the app

Future deployments are automatic (`autoDeploy: true` in render.yaml):
- Push to the connected branch → Render rebuilds the backend and runs `alembic upgrade head`
- Push to main (or the connected branch) → Vercel rebuilds the frontend

---

## Known limitations of free tier

| Limitation | Impact |
|-----------|--------|
| Render free web service **spins down after 15 min of inactivity** | First request after idle takes ~30–60 seconds. Warn your client — this is normal on free tier. |
| Render free PostgreSQL is **deleted after 90 days** | Back up data before the 90-day mark. Upgrade to a paid DB plan for permanent storage. |
| Render free tier has **limited CPU/RAM** | Fine for UAT; not suitable for production loads. |

---

## Upgrading to DigitalOcean (production)

When ready to move off free tier:

1. Provision a new DigitalOcean Droplet and PostgreSQL database
2. Copy all env vars from Render to the Droplet's `.env` file (use `.env.production.example` as a template)
3. Point `DATABASE_URL` at the new DB and run `alembic upgrade head`
4. Use the existing `deploy.sh` script: `./deploy.sh <droplet-ip>`
5. Update `VITE_API_URL` in Vercel to the new backend URL and redeploy

---

## Troubleshooting

**CORS errors in the browser**
- Check that `ALLOWED_ORIGINS` on Render includes the exact Vercel URL (no trailing slash)
- Check Render logs for startup errors

**`alembic upgrade head` fails on first deploy**
- Usually means `DATABASE_URL` is not set or the DB isn't ready yet
- Wait 1–2 minutes after the DB is created, then trigger a manual deploy

**Frontend shows blank page / 404 on page refresh**
- The `vercel.json` rewrite rule handles SPA routing — if this happens, verify `vercel.json` was picked up

**API calls return 502/503**
- Render free tier may be waking up (cold start) — retry after 30 seconds
