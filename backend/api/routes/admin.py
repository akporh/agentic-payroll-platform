from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="backend/api/templates")


@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )

@router.get("/admin/onboarding", response_class=HTMLResponse)
async def admin_onboarding(request: Request):
    return templates.TemplateResponse(
        "onboarding.html",
        {"request": request}
    )

@router.get("/admin/payroll", response_class=HTMLResponse)
async def admin_payroll(request: Request):
    return templates.TemplateResponse(
        "payroll.html",
        {"request": request}
    )
