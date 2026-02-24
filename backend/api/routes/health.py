"""
Health check route.

Returns service status for monitoring and readiness probes.
No database access. No side effects.

Reference: ARCHITECTURE_LOCK.md — API Layer.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    """Return service health status.

    Returns:
        Dict with status, service name, and current phase.
    """
    return {
        "status": "ok",
        "service": "agentic-payroll-platform",
        "phase": "phase1",
    }
