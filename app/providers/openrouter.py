import os

import httpx


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class OpenRouterError(Exception):
    pass


async def get_key_info() -> dict:
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise OpenRouterError(
            "OPENROUTER_API_KEY belum dikonfigurasi."
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{OPENROUTER_BASE_URL}/key",
                headers=headers,
            )

    except httpx.RequestError as exc:
        raise OpenRouterError(
            f"Gagal terhubung ke OpenRouter: {exc}"
        ) from exc

    if response.status_code == 401:
        raise OpenRouterError(
            "API key OpenRouter tidak valid."
        )

    if not response.is_success:
        raise OpenRouterError(
            f"OpenRouter mengembalikan HTTP "
            f"{response.status_code}."
        )

    payload = response.json()

    return payload.get("data", {})
