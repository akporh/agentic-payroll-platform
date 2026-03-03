"""
FastAPI application entry point.

Creates the app instance and registers versioned API routers.
No business logic lives here — this is purely the HTTP entry layer.

Reference: ARCHITECTURE_LOCK.md — API Layer.
"""

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from backend.api.routes.health import router as health_router
from backend.api.routes.onboarding import router as onboarding_router
from backend.api.routes.onboarding_validation import router as onboarding_validation_router
from backend.api.routes import admin
from backend.api.routes import payroll
from backend.api.routes import workspace

app = FastAPI(
    title="Agentic Payroll Platform",
    description="Phase 1 MVP — Deterministic payroll engine for Nigerian payroll processing",
    version="1.0.0",
)

templates = Jinja2Templates(directory="backend/api/templates")


app.include_router(admin.router)
app.mount("/static", StaticFiles(directory="backend/api/static"), name="static")


app.include_router(health_router, prefix="/api/v1")
app.include_router(onboarding_router, prefix="/api/v1")
app.include_router(onboarding_validation_router, prefix="/api/v1")
app.include_router(payroll.router, prefix="/api/v1")
app.include_router(workspace.router, prefix="/api/v1")