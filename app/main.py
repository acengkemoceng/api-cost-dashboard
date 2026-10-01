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
    get_balance_history,
    get_history,
    init_db,
    save_balance_snapshot,
    save_snapshot,
)

from app.providers.openrouter import (
    OpenRouterError,
    get_credits,
    get_key_info,
)

from app.providers.deepseek import (
    DeepSeekError,
    get_balance as get_deepseek_balance,
)

from app.providers.agentrouter import (
    AgentRouterError,
    get_models as get_agentrouter_models,
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

        return max(
            interval,
            10,
        )

    except ValueError:
        return 900


def get_deepseek_usd_balance(
    data: dict,
) -> dict | None:

    balances = data.get(
        "balance_infos",
        [],
    )

    return next(
        (
            item
            for item in balances
            if item.get("currency") == "USD"
        ),
        None,
    )


async def collect_openrouter(
    app: FastAPI,
):
    status = app.state.collectors[
        "openrouter"
    ]

    status["last_attempt"] = utc_now()

    try:
        data = await get_key_info()

        inserted = await save_snapshot(
            "openrouter",
            data,
        )

        status["last_success"] = utc_now()
        status["last_inserted"] = inserted
        status["last_error"] = None

        logger.info(
            "OpenRouter snapshot checked. "
            "New snapshot: %s",
            inserted,
        )

    except OpenRouterError as exc:

        status["last_error"] = str(exc)

        logger.warning(
            "OpenRouter collector error: %s",
            exc,
        )

    except Exception as exc:

        status["last_error"] = str(exc)

        logger.exception(
            "Unexpected OpenRouter "
            "collector error"
        )


async def collect_deepseek(
    app: FastAPI,
):
    status = app.state.collectors[
        "deepseek"
    ]

    status["last_attempt"] = utc_now()

    try:
        data = await get_deepseek_balance()

        usd = get_deepseek_usd_balance(
            data
        )

        if usd is None:
            raise DeepSeekError(
                "Saldo USD tidak ditemukan."
            )

        inserted = (
            await save_balance_snapshot(
                provider="deepseek",
                currency="USD",
                total_balance=float(
                    usd.get(
                        "total_balance"
                    )
                    or 0
                ),
                topped_up_balance=float(
                    usd.get(
                        "topped_up_balance"
                    )
                    or 0
                ),
                granted_balance=float(
                    usd.get(
                        "granted_balance"
                    )
                    or 0
                ),
            )
        )

        status["last_success"] = utc_now()
        status["last_inserted"] = inserted
        status["last_error"] = None

        logger.info(
            "DeepSeek balance checked. "
            "New snapshot: %s",
            inserted,
        )

    except DeepSeekError as exc:

        status["last_error"] = str(exc)

        logger.warning(
            "DeepSeek collector error: %s",
            exc,
        )

    except Exception as exc:

        status["last_error"] = str(exc)

        logger.exception(
            "Unexpected DeepSeek "
            "collector error"
        )


async def provider_collector(
    app: FastAPI,
):
    interval = get_snapshot_interval()

    logger.info(
        "Provider collector started "
        "with interval %s seconds",
        interval,
    )

    while True:

        await collect_openrouter(app)

        await collect_deepseek(app)

        await asyncio.sleep(
            interval
        )


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    await init_db()

    app.state.collectors = {
        "openrouter": {
            "last_attempt": None,
            "last_success": None,
            "last_inserted": None,
            "last_error": None,
        },
        "deepseek": {
            "last_attempt": None,
            "last_success": None,
            "last_inserted": None,
            "last_error": None,
        },
    }

    collector_task = (
        asyncio.create_task(
            provider_collector(app)
        )
    )

    yield

    collector_task.cancel()

    try:
        await collector_task

    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="AI API Cost Dashboard",
    version="0.7.0",
    description=(
        "Dashboard untuk memonitor biaya, "
        "saldo, dan penggunaan AI API."
    ),
    lifespan=lifespan,
)


app.mount(
    "/static",
    StaticFiles(
        directory="app/static"
    ),
    name="static",
)


templates = Jinja2Templates(
    directory="app/templates",
)


@app.get(
    "/",
    response_class=HTMLResponse,
)
async def dashboard(
    request: Request,
):

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

    credits = {
        "connected": False,
        "total_credits": 0,
        "total_usage": 0,
        "remaining": 0,
        "usage_percent": 0,
        "error": None,
    }

    deepseek = {
        "connected": False,
        "is_available": False,
        "currency": "USD",
        "total_balance": 0,
        "topped_up_balance": 0,
        "granted_balance": 0,
        "error": None,
    }

    # OpenRouter key usage
    try:
        data = await get_key_info()

        openrouter.update(
            {
                "connected": True,
                "label": data.get(
                    "label"
                ),
                "is_free_tier": data.get(
                    "is_free_tier"
                ),
                "usage": (
                    data.get(
                        "usage"
                    )
                    or 0
                ),
                "usage_daily": (
                    data.get(
                        "usage_daily"
                    )
                    or 0
                ),
                "usage_weekly": (
                    data.get(
                        "usage_weekly"
                    )
                    or 0
                ),
                "usage_monthly": (
                    data.get(
                        "usage_monthly"
                    )
                    or 0
                ),
                "limit": data.get(
                    "limit"
                ),
                "limit_remaining": (
                    data.get(
                        "limit_remaining"
                    )
                ),
            }
        )

    except OpenRouterError as exc:
        openrouter["error"] = str(exc)

    # OpenRouter account credits
    try:
        credit_data = await get_credits()

        total_credits = float(
            credit_data.get(
                "total_credits"
            )
            or 0
        )

        total_usage = float(
            credit_data.get(
                "total_usage"
            )
            or 0
        )

        remaining = max(
            total_credits
            - total_usage,
            0,
        )

        usage_percent = 0

        if total_credits > 0:

            usage_percent = min(
                (
                    total_usage
                    / total_credits
                )
                * 100,
                100,
            )

        credits.update(
            {
                "connected": True,
                "total_credits": (
                    total_credits
                ),
                "total_usage": (
                    total_usage
                ),
                "remaining": remaining,
                "usage_percent": (
                    usage_percent
                ),
            }
        )

    except OpenRouterError as exc:
        credits["error"] = str(exc)

    # DeepSeek balance
    try:
        deepseek_data = (
            await get_deepseek_balance()
        )

        usd = get_deepseek_usd_balance(
            deepseek_data
        )

        deepseek["connected"] = True

        deepseek["is_available"] = (
            deepseek_data.get(
                "is_available",
                False,
            )
        )

        if usd:

            deepseek.update(
                {
                    "currency": "USD",

                    "total_balance": float(
                        usd.get(
                            "total_balance"
                        )
                        or 0
                    ),

                    "topped_up_balance": float(
                        usd.get(
                            "topped_up_balance"
                        )
                        or 0
                    ),

                    "granted_balance": float(
                        usd.get(
                            "granted_balance"
                        )
                        or 0
                    ),
                }
            )

    except DeepSeekError as exc:
        deepseek["error"] = str(exc)

    connected_providers = sum(
        [
            (
                1
                if openrouter[
                    "connected"
                ]
                else 0
            ),
            (
                1
                if deepseek[
                    "connected"
                ]
                else 0
            ),
        ]
    )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "app_name": (
                "AI API Cost Dashboard"
            ),
            "version": "0.7.0",
            "connected_providers": (
                connected_providers
            ),
            "openrouter": openrouter,
            "credits": credits,
            "deepseek": deepseek,
        },
    )


@app.get("/health")
async def health():

    return {
        "status": "ok",
        "service": (
            "ai-api-cost-dashboard"
        ),
        "version": "0.7.0",
    }


@app.get(
    "/api/providers/openrouter"
)
async def openrouter_status():

    try:
        data = await get_key_info()

        return {
            "provider": "openrouter",
            "connected": True,
            "label": data.get(
                "label"
            ),
            "is_free_tier": (
                data.get(
                    "is_free_tier"
                )
            ),
            "usage": data.get(
                "usage"
            ),
            "usage_daily": data.get(
                "usage_daily"
            ),
            "usage_weekly": data.get(
                "usage_weekly"
            ),
            "usage_monthly": data.get(
                "usage_monthly"
            ),
            "limit": data.get(
                "limit"
            ),
            "limit_remaining": (
                data.get(
                    "limit_remaining"
                )
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


@app.get(
    "/api/providers/openrouter/credits"
)
async def openrouter_credits():

    try:
        data = await get_credits()

        total_credits = float(
            data.get(
                "total_credits"
            )
            or 0
        )

        total_usage = float(
            data.get(
                "total_usage"
            )
            or 0
        )

        remaining = max(
            total_credits
            - total_usage,
            0,
        )

        return {
            "provider": "openrouter",
            "connected": True,
            "total_credits": (
                total_credits
            ),
            "total_usage": (
                total_usage
            ),
            "remaining": remaining,
        }

    except OpenRouterError as exc:

        return {
            "provider": "openrouter",
            "connected": False,
            "error": str(exc),
        }


@app.get(
    "/api/providers/deepseek"
)
async def deepseek_status():

    try:
        data = (
            await get_deepseek_balance()
        )

        balances = data.get(
            "balance_infos",
            [],
        )

        normalized = []

        for item in balances:

            normalized.append(
                {
                    "currency": (
                        item.get(
                            "currency"
                        )
                    ),

                    "total_balance": float(
                        item.get(
                            "total_balance"
                        )
                        or 0
                    ),

                    "granted_balance": float(
                        item.get(
                            "granted_balance"
                        )
                        or 0
                    ),

                    "topped_up_balance": float(
                        item.get(
                            "topped_up_balance"
                        )
                        or 0
                    ),
                }
            )

        primary = next(
            (
                item
                for item in normalized
                if item[
                    "currency"
                ] == "USD"
            ),
            (
                normalized[0]
                if normalized
                else None
            ),
        )

        return {
            "provider": "deepseek",
            "connected": True,
            "is_available": (
                data.get(
                    "is_available",
                    False,
                )
            ),
            "primary_balance": (
                primary
            ),
            "balances": normalized,
        }

    except DeepSeekError as exc:

        return {
            "provider": "deepseek",
            "connected": False,
            "error": str(exc),
        }


@app.get(
    "/api/history/openrouter"
)
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


@app.get(
    "/api/history/deepseek"
)
async def deepseek_history(
    limit: int = 30,
):

    history = (
        await get_balance_history(
            provider="deepseek",
            currency="USD",
            limit=limit,
        )
    )

    return {
        "provider": "deepseek",
        "currency": "USD",
        "count": len(history),
        "data": history,
    }


@app.get(
    "/api/collector/status"
)
async def collector_status():

    return {
        "interval_seconds": (
            get_snapshot_interval()
        ),
        "providers": (
            app.state.collectors
        ),
    }

@app.get(
    "/api/providers/agentrouter"
)
async def agentrouter_status():

    try:
        models = (
            await get_agentrouter_models()
        )

        model_ids = []

        for model in models:
            model_id = model.get("id")

            if model_id:
                model_ids.append(
                    model_id
                )

        return {
            "provider": "agentrouter",
            "connected": True,
            "base_url": (
                "https://co.agentrouter.org/v1"
            ),
            "model_count": len(
                model_ids
            ),
            "models": model_ids,
        }

    except AgentRouterError as exc:

        return {
            "provider": "agentrouter",
            "connected": False,
            "error": str(exc),
        }
