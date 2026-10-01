import os

import httpx


DEEPSEEK_BASE_URL = "https://api.deepseek.com"


class DeepSeekError(Exception):
    pass


async def get_balance() -> dict:
    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        raise DeepSeekError(
            "DEEPSEEK_API_KEY belum dikonfigurasi."
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
                f"{DEEPSEEK_BASE_URL}/user/balance",
                headers=headers,
            )

    except httpx.RequestError as exc:
        raise DeepSeekError(
            f"Gagal terhubung ke DeepSeek: {exc}"
        ) from exc

    if response.status_code == 401:
        raise DeepSeekError(
            "API key DeepSeek tidak valid."
        )

    if response.status_code == 403:
        raise DeepSeekError(
            "API key DeepSeek tidak memiliki izin."
        )

    if not response.is_success:
        raise DeepSeekError(
            "DeepSeek mengembalikan HTTP "
            f"{response.status_code}."
        )

    return response.json()
