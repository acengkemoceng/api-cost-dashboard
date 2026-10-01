from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.providers.openrouter import (
    OpenRouterError,
    get_key_info,
)


app = FastAPI(
    title="AI API Cost Dashboard",
    version="0.2.0",
    description="Dashboard untuk memonitor biaya dan penggunaan AI API.",
)


app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    openrouter = {
        "connected": False,
        "label": None,
        "is_free_tier": None,
        "usage": 0,
        "usage_daily": 0,
        "usage_weekly": 0,
        "usage_monthly": 0,
        "limit": None,
        "limit_remaining": None,
        "error": None,
    }

    try:
        data = await get_key_info()

        openrouter.update(
            {
                "connected": True,
                "label": data.get("label"),
                "is_free_tier": data.get("is_free_tier"),
                "usage": data.get("usage") or 0,
                "usage_daily": data.get("usage_daily") or 0,
                "usage_weekly": data.get("usage_weekly") or 0,
                "usage_monthly": data.get("usage_monthly") or 0,
                "limit": data.get("limit"),
                "limit_remaining": data.get("limit_remaining"),
            }
        )

    except OpenRouterError as exc:
        openrouter["error"] = str(exc)

    connected_providers = 1 if openrouter["connected"] else 0

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "app_name": "AI API Cost Dashboard",
            "version": "0.2.0",
            "connected_providers": connected_providers,
            "openrouter": openrouter,
        },
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "ai-api-cost-dashboard",
        "version": "0.2.0",
    }


@app.get("/api/providers/openrouter")
async def openrouter_status():
    try:
        data = await get_key_info()

        return {
            "provider": "openrouter",
            "connected": True,
            "label": data.get("label"),
            "is_free_tier": data.get("is_free_tier"),
            "usage": data.get("usage"),
            "usage_daily": data.get("usage_daily"),
            "usage_weekly": data.get("usage_weekly"),
            "usage_monthly": data.get("usage_monthly"),
            "limit": data.get("limit"),
            "limit_remaining": data.get("limit_remaining"),
            "limit_reset": data.get("limit_reset"),
        }

    except OpenRouterError as exc:
        return {
            "provider": "openrouter",
            "connected": False,
            "error": str(exc),
        }
