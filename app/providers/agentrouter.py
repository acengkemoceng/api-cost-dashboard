import os

import httpx


AGENTROUTER_BASE_URL = "https://agentrouter.org/v1"


class AgentRouterError(Exception):
    pass


async def get_models() -> list[dict]:
    api_key = os.getenv(
        "AGENTROUTER_API_KEY"
    )

    if not api_key:
        raise AgentRouterError(
            "AGENTROUTER_API_KEY belum dikonfigurasi."
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    try:
        async with httpx.AsyncClient(
            timeout=20.0
        ) as client:

            response = await client.get(
                f"{AGENTROUTER_BASE_URL}/models",
                headers=headers,
            )

    except httpx.RequestError as exc:
        raise AgentRouterError(
            f"Gagal terhubung ke AgentRouter: {exc}"
        ) from exc

    if not response.is_success:

        detail = response.text[:400]

        raise AgentRouterError(
            f"HTTP {response.status_code}: {detail}"
        )

    payload = response.json()

    models = payload.get(
        "data",
        [],
    )

    if not isinstance(models, list):
        raise AgentRouterError(
            "Format daftar model AgentRouter tidak dikenali."
        )

    return models
