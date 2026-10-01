import asyncio
import logging
import os

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import (
    get_history,
    init_db,
    save_snapshot,
)
from app.providers.openrouter import (
    OpenRouterError,
    get_credits,
    get_key_info,
)


logger = logging.getLogger(__name__)


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def get_snapshot_interval() -> int:
    try:
        interval = int(
            os.getenv(
                "SNAPSHOT_INTERVAL_SECONDS",
                "900",
            )
        )

        return max(interval, 10)

    except ValueError:
        return 900


async def openrouter_collector(app: FastAPI):
    interval = get_snapshot_interval()

    logger.info(
        "OpenRouter collector started "
        "with interval %s seconds",
        interval,
    )

    while True:
        app.state.collector_last_attempt = (
            utc_now()
        )

        try:
            data = await get_key_info()

            inserted = await save_snapshot(
                "openrouter",
                data,
            )

            app.state.collector_last_success = (
                utc_now()
            )

            app.state.collector_last_inserted = (
                inserted
            )

            app.state.collector_last_error = None

            logger.info(
                "OpenRouter snapshot checked. "
                "New snapshot: %s",
                inserted,
            )

        except OpenRouterError as exc:
            app.state.collector_last_error = (
                str(exc)
            )

            logger.warning(
                "OpenRouter collector error: %s",
                exc,
            )

        except Exception as exc:
            app.state.collector_last_error = (
                str(exc)
            )

            logger.exception(
                "Unexpected collector error"
            )

        await asyncio.sleep(interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    app.state.collector_last_attempt = None
    app.state.collector_last_success = None
    app.state.collector_last_inserted = None
    app.state.collector_last_error = None

    collector_task = asyncio.create_task(
        openrouter_collector(app)
    )

    yield

    collector_task.cancel()

    try:
        await collector_task

    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="AI API Cost Dashboard",
    version="0.4.0",
    description=(
        "Dashboard untuk memonitor biaya "
        "dan penggunaan AI API."
    ),
    lifespan=lifespan,
)


app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

templates = Jinja2Templates(
    directory="app/templates",
)


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
                "is_free_tier": data.get(
                    "is_free_tier"
                ),
                "usage": (
                    data.get("usage") or 0
                ),
                "usage_daily": (
                    data.get("usage_daily") or 0
                ),
                "usage_weekly": (
                    data.get("usage_weekly") or 0
                ),
                "usage_monthly": (
                    data.get("usage_monthly") or 0
                ),
                "limit": data.get("limit"),
                "limit_remaining": data.get(
                    "limit_remaining"
                ),
            }
        )

    except OpenRouterError as exc:
        openrouter["error"] = str(exc)

    connected_providers = (
        1 if openrouter["connected"] else 0
    )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "app_name": (
                "AI API Cost Dashboard"
            ),
            "version": "0.4.0",
            "connected_providers": (
                connected_providers
            ),
            "openrouter": openrouter,
        },
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": (
            "ai-api-cost-dashboard"
        ),
        "version": "0.4.0",
    }


@app.get("/api/providers/openrouter")
async def openrouter_status():

    try:
        data = await get_key_info()

        return {
            "provider": "openrouter",
            "connected": True,
            "label": data.get("label"),
            "is_free_tier": data.get(
                "is_free_tier"
            ),
            "usage": data.get("usage"),
            "usage_daily": data.get(
                "usage_daily"
            ),
            "usage_weekly": data.get(
                "usage_weekly"
            ),
            "usage_monthly": data.get(
                "usage_monthly"
            ),
            "limit": data.get("limit"),
            "limit_remaining": data.get(
                "limit_remaining"
            ),
            "limit_reset": data.get(
                "limit_reset"
            ),
        }

    except OpenRouterError as exc:
        return {
            "provider": "openrouter",
            "connected": False,
            "error": str(exc),
        }


@app.get("/api/history/openrouter")
async def openrouter_history(
    limit: int = 30,
):

    history = await get_history(
        "openrouter",
        limit,
    )

    return {
        "provider": "openrouter",
        "count": len(history),
        "data": history,
    }


@app.get("/api/collector/status")
async def collector_status():

    return {
        "provider": "openrouter",
        "interval_seconds": (
            get_snapshot_interval()
        ),
        "last_attempt": (
            app.state.collector_last_attempt
        ),
        "last_success": (
            app.state.collector_last_success
        ),
        "last_inserted": (
            app.state.collector_last_inserted
        ),
        "last_error": (
            app.state.collector_last_error
        ),
    }

@app.get("/api/providers/openrouter/credits")
async def openrouter_credits():

    try:
        data = await get_credits()

        total_credits = float(
            data.get("total_credits") or 0
        )

        total_usage = float(
            data.get("total_usage") or 0
        )

        remaining = max(
            total_credits - total_usage,
            0,
        )

        return {
            "provider": "openrouter",
            "connected": True,
            "total_credits": total_credits,
            "total_usage": total_usage,
            "remaining": remaining,
        }

    except OpenRouterError as exc:
        return {
            "provider": "openrouter",
            "connected": False,
            "error": str(exc),
        }
