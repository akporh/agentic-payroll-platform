"""
FastAPI application entry point.

Creates the app instance and registers versioned API routers.
No business logic lives here — this is purely the HTTP entry layer.

Reference: ARCHITECTURE_LOCK.md — API Layer.
"""

from fastapi import FastAPI
from backend.api.routes.health import router as health_router
from backend.api.routes.onboarding import router as onboarding_router
from backend.api.routes.onboarding_validation import router as onboarding_validation_router

app = FastAPI(
    title="Agentic Payroll Platform",
    description="Phase 1 MVP — Deterministic payroll engine for Nigerian payroll processing",
    version="1.0.0",
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(onboarding_router, prefix="/api/v1")
app.include_router(onboarding_validation_router, prefix="/api/v1")
