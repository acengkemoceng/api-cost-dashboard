import os

from datetime import (
    datetime,
    timedelta,
    timezone,
)


def is_demo_mode() -> bool:
    value = os.getenv(
        "DEMO_MODE",
        "false",
    )

    return value.lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def get_demo_analytics() -> dict:
    return {
        "available": True,
        "period_days": 30,

        "request_count": 1284,
        "total_usage": 7.4628,

        "total_tokens": 2814300,
        "input_tokens": 1820500,
        "output_tokens": 993800,

        "reasoning_tokens": 214500,
        "cached_tokens": 438200,

        "avg_cost_per_request": (
            7.4628 / 1284
        ),

        "avg_cost_per_1k_tokens": (
            7.4628
            / 2814300
            * 1000
        ),

        "top_models": [
            {
                "model": "demo/model-alpha",
                "requests": 584,
                "tokens": 1312200,
                "input_tokens": 860000,
                "output_tokens": 452200,
                "cost": 3.1428,
            },
            {
                "model": "demo/model-beta",
                "requests": 421,
                "tokens": 927100,
                "input_tokens": 591000,
                "output_tokens": 336100,
                "cost": 2.4810,
            },
            {
                "model": "demo/model-gamma",
                "requests": 279,
                "tokens": 575000,
                "input_tokens": 369500,
                "output_tokens": 205500,
                "cost": 1.8390,
            },
        ],

        "error": None,
    }


def get_demo_dashboard_state(
    registry: list[dict],
) -> dict:

    analytics = get_demo_analytics()

    openrouter = {
        "connected": True,
        "configured": True,
        "label": "demo-openrouter-key",
        "is_free_tier": False,

        "usage": 7.4628,
        "usage_daily": 0.3842,
        "usage_weekly": 2.1734,
        "usage_monthly": 7.4628,

        "error": None,
    }

    credits = {
        "connected": True,

        "total_credits": 25.0,
        "total_usage": 7.4628,
        "remaining": 17.5372,

        "usage_percent": (
            7.4628
            / 25.0
            * 100
        ),

        "error": None,
    }

    deepseek = {
        "connected": True,
        "configured": True,
        "is_available": True,

        "currency": "USD",

        "total_balance": 6.12,
        "topped_up_balance": 6.12,
        "granted_balance": 0.0,

        "error": None,
    }

    integrations = []

    for provider in registry:
        item = dict(provider)

        if provider["id"] in {
            "openrouter",
            "deepseek",
        }:
            item["connected"] = True
            item["configured"] = True
            item["status"] = "connected"

        else:
            item["connected"] = False
            item["status"] = "not_configured"

        integrations.append(
            item
        )

    total_balance = (
        credits["remaining"]
        + deepseek["total_balance"]
    )

    summary = {
        "total_balance": total_balance,

        "active_providers": 2,

        "integration_count": len(
            integrations
        ),

        "template_count": sum(
            1
            for provider in integrations
            if provider["template"]
        ),

        "tracked_spend": (
            analytics["total_usage"]
        ),

        "tracked_requests": (
            analytics["request_count"]
        ),

        "tracked_tokens": (
            analytics["total_tokens"]
        ),

        "avg_cost_per_request": (
            analytics[
                "avg_cost_per_request"
            ]
        ),
    }

    return {
        "demo_mode": True,

        "summary": summary,

        "openrouter": openrouter,
        "credits": credits,
        "analytics": analytics,
        "deepseek": deepseek,

        "integrations": integrations,
    }


def get_demo_openrouter_history() -> list[dict]:
    now = datetime.now(
        timezone.utc
    )

    values = [
        1.18,
        2.05,
        3.14,
        4.22,
        5.63,
        6.51,
        7.46,
    ]

    history = []

    for index, value in enumerate(
        values
    ):
        date = now - timedelta(
            days=(
                len(values)
                - index
                - 1
            )
            * 4
        )

        history.append(
            {
                "id": index + 1,
                "provider": "openrouter",

                "usage_total": value,
                "usage_daily": (
                    value / 20
                ),
                "usage_weekly": (
                    value / 4
                ),
                "usage_monthly": value,

                "limit_amount": None,
                "limit_remaining": None,

                "created_at": (
                    date.isoformat()
                ),
            }
        )

    return history


def get_demo_deepseek_history() -> list[dict]:
    now = datetime.now(
        timezone.utc
    )

    values = [
        9.50,
        9.04,
        8.41,
        7.92,
        7.13,
        6.71,
        6.12,
    ]

    history = []

    for index, value in enumerate(
        values
    ):
        date = now - timedelta(
            days=(
                len(values)
                - index
                - 1
            )
            * 4
        )

        history.append(
            {
                "id": index + 1,
                "provider": "deepseek",
                "currency": "USD",

                "total_balance": value,
                "topped_up_balance": value,
                "granted_balance": 0.0,

                "created_at": (
                    date.isoformat()
                ),
            }
        )

    return history
