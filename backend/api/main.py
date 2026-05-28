"""
FastAPI application entry point.

Creates the app instance and registers versioned API routers.
No business logic lives here — this is purely the HTTP entry layer.

Reference: ARCHITECTURE_LOCK.md — API Layer.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from backend.api.routes.health import router as health_router
from backend.api.routes.onboarding import router as onboarding_router
from backend.api.routes.onboarding_validation import router as onboarding_validation_router
from backend.api.routes import admin
from backend.api.routes import payroll
from backend.api.routes import payroll_input
from backend.api.routes import workspace
from backend.api.routes import employees

app = FastAPI(
    title="Agentic Payroll Platform",
    description="Phase 1 MVP — Deterministic payroll engine for Nigerian payroll processing",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS — required so the Vercel-hosted frontend can call this backend.
# ALLOWED_ORIGINS env var: comma-separated list of allowed origins.
# Defaults to "*" for UAT/preview. Tighten to the Vercel URL in production.
# Example: ALLOWED_ORIGINS=https://payroll.example.com,https://payroll-git-main.vercel.app
# ---------------------------------------------------------------------------
_raw_origins = os.environ.get("ALLOWED_ORIGINS", "*")
_origins = [o.strip() for o in _raw_origins.split(",")] if _raw_origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="backend/api/templates")


app.include_router(admin.router)
app.mount("/static", StaticFiles(directory="backend/api/static"), name="static")


app.include_router(health_router, prefix="/api/v1")
app.include_router(onboarding_router, prefix="/api/v1")
app.include_router(onboarding_validation_router, prefix="/api/v1")
app.include_router(payroll.router, prefix="/api/v1")
app.include_router(payroll_input.router, prefix="/api/v1")
app.include_router(workspace.router, prefix="/api/v1")
app.include_router(employees.router, prefix="/api/v1")