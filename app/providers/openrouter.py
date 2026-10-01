import asyncio
import os

from datetime import (
    datetime,
    timedelta,
    timezone,
)

import httpx


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class OpenRouterError(Exception):
    pass


def _credential(env_key: str) -> str:
    value = os.getenv(env_key)

    if not value:
        raise OpenRouterError(
            f"{env_key} belum dikonfigurasi."
        )

    return value


async def _request(
    method: str,
    endpoint: str,
    env_key: str,
    json: dict | None = None,
) -> dict:

    api_key = _credential(env_key)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.request(
                method,
                f"{OPENROUTER_BASE_URL}{endpoint}",
                headers=headers,
                json=json,
            )

    except httpx.RequestError as exc:
        raise OpenRouterError(
            f"Gagal terhubung ke OpenRouter: {exc}"
        ) from exc

    if response.status_code == 401:
        raise OpenRouterError(
            "Credential OpenRouter tidak valid."
        )

    if response.status_code == 403:
        raise OpenRouterError(
            "Credential tidak memiliki izin. "
            "Analytics membutuhkan Management Key."
        )

    if not response.is_success:

        detail = response.text[:300]

        raise OpenRouterError(
            f"OpenRouter HTTP "
            f"{response.status_code}: {detail}"
        )

    try:
        return response.json()

    except ValueError as exc:
        raise OpenRouterError(
            "Response OpenRouter bukan JSON valid."
        ) from exc


async def get_key_info() -> dict:

    payload = await _request(
        "GET",
        "/key",
        "OPENROUTER_API_KEY",
    )

    return payload.get(
        "data",
        {},
    )


async def get_credits() -> dict:

    payload = await _request(
        "GET",
        "/credits",
        "OPENROUTER_MANAGEMENT_KEY",
    )

    return payload.get(
        "data",
        {},
    )


async def get_analytics_meta() -> dict:

    return await _request(
        "GET",
        "/analytics/meta",
        "OPENROUTER_MANAGEMENT_KEY",
    )


async def query_analytics(
    metrics: list[str],
    dimensions: list[str] | None = None,
    days: int = 30,
    order_by: dict | None = None,
    limit: int = 100,
) -> dict:

    now = datetime.now(
        timezone.utc
    )

    start = now - timedelta(
        days=max(
            1,
            min(days, 365),
        )
    )

    body = {
        "metrics": metrics,

        "time_range": {
            "start": (
                start.isoformat()
                .replace("+00:00", "Z")
            ),
            "end": (
                now.isoformat()
                .replace("+00:00", "Z")
            ),
        },

        "limit": max(
            1,
            min(limit, 10000),
        ),
    }

    if dimensions:
        body["dimensions"] = dimensions

    if order_by:
        body["order_by"] = order_by

    return await _request(
        "POST",
        "/analytics/query",
        "OPENROUTER_MANAGEMENT_KEY",
        json=body,
    )


def _extract_rows(
    payload: dict,
) -> tuple[list[dict], dict]:

    outer = payload.get(
        "data",
        {},
    )

    if not isinstance(
        outer,
        dict,
    ):
        return [], {}

    rows = outer.get(
        "data",
        [],
    )

    metadata = outer.get(
        "metadata",
        {},
    )

    if not isinstance(
        rows,
        list,
    ):
        rows = []

    if not isinstance(
        metadata,
        dict,
    ):
        metadata = {}

    return rows, metadata


def _as_int(
    value,
) -> int:

    try:
        return int(
            float(
                value or 0
            )
        )

    except (
        TypeError,
        ValueError,
    ):
        return 0


def _as_float(
    value,
) -> float:

    try:
        return float(
            value or 0
        )

    except (
        TypeError,
        ValueError,
    ):
        return 0.0


async def get_analytics_dashboard(
    days: int = 30,
) -> dict:

    metrics = [
        "request_count",
        "total_usage",
        "tokens_total",
        "tokens_prompt",
        "tokens_completion",
        "reasoning_tokens",
        "cached_tokens",
    ]

    summary_query = query_analytics(
        metrics=metrics,
        days=days,
        limit=1,
    )

    models_query = query_analytics(
        metrics=[
            "request_count",
            "total_usage",
            "tokens_total",
            "tokens_prompt",
            "tokens_completion",
        ],
        dimensions=[
            "model",
        ],
        days=days,
        order_by={
            "field": "total_usage",
            "direction": "desc",
        },
        limit=10,
    )

    (
        summary_payload,
        models_payload,
    ) = await asyncio.gather(
        summary_query,
        models_query,
    )

    summary_rows, summary_meta = (
        _extract_rows(
            summary_payload
        )
    )

    model_rows, model_meta = (
        _extract_rows(
            models_payload
        )
    )

    row = (
        summary_rows[0]
        if summary_rows
        else {}
    )

    request_count = _as_int(
        row.get(
            "request_count"
        )
    )

    total_usage = _as_float(
        row.get(
            "total_usage"
        )
    )

    total_tokens = _as_int(
        row.get(
            "tokens_total"
        )
    )

    prompt_tokens = _as_int(
        row.get(
            "tokens_prompt"
        )
    )

    completion_tokens = _as_int(
        row.get(
            "tokens_completion"
        )
    )

    reasoning_tokens = _as_int(
        row.get(
            "reasoning_tokens"
        )
    )

    cached_tokens = _as_int(
        row.get(
            "cached_tokens"
        )
    )

    avg_cost_per_request = 0.0

    if request_count > 0:
        avg_cost_per_request = (
            total_usage
            / request_count
        )

    avg_cost_per_1k_tokens = 0.0

    if total_tokens > 0:
        avg_cost_per_1k_tokens = (
            total_usage
            / total_tokens
            * 1000
        )

    models = []

    for item in model_rows:

        models.append(
            {
                "model": (
                    item.get(
                        "model"
                    )
                    or "Unknown"
                ),

                "requests": _as_int(
                    item.get(
                        "request_count"
                    )
                ),

                "tokens": _as_int(
                    item.get(
                        "tokens_total"
                    )
                ),

                "input_tokens": _as_int(
                    item.get(
                        "tokens_prompt"
                    )
                ),

                "output_tokens": _as_int(
                    item.get(
                        "tokens_completion"
                    )
                ),

                "cost": _as_float(
                    item.get(
                        "total_usage"
                    )
                ),
            }
        )

    return {
        "period_days": days,

        "request_count": (
            request_count
        ),

        "total_usage": (
            total_usage
        ),

        "total_tokens": (
            total_tokens
        ),

        "input_tokens": (
            prompt_tokens
        ),

        "output_tokens": (
            completion_tokens
        ),

        "reasoning_tokens": (
            reasoning_tokens
        ),

        "cached_tokens": (
            cached_tokens
        ),

        "avg_cost_per_request": (
            avg_cost_per_request
        ),

        "avg_cost_per_1k_tokens": (
            avg_cost_per_1k_tokens
        ),

        "top_models": models,

        "metadata": {
            "summary": (
                summary_meta
            ),
            "models": (
                model_meta
            ),
        },
    }
