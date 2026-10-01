import os

import httpx


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class OpenRouterError(Exception):
    pass


async def _get(
    endpoint: str,
    env_key: str,
) -> dict:

    api_key = os.getenv(env_key)

    if not api_key:
        raise OpenRouterError(
            f"{env_key} belum dikonfigurasi."
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    try:
        async with httpx.AsyncClient(
            timeout=15.0
        ) as client:

            response = await client.get(
                f"{OPENROUTER_BASE_URL}{endpoint}",
                headers=headers,
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
            "Credential OpenRouter tidak memiliki izin."
        )

    if not response.is_success:
        raise OpenRouterError(
            "OpenRouter mengembalikan HTTP "
            f"{response.status_code}."
        )

    payload = response.json()

    return payload.get("data", {})


async def get_key_info() -> dict:
    return await _get(
        "/key",
        "OPENROUTER_API_KEY",
    )


async def get_credits() -> dict:
    return await _get(
        "/credits",
        "OPENROUTER_MANAGEMENT_KEY",
    )
