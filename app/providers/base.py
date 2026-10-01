from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ProviderCapabilities:
    balance: bool = False
    cost: bool = False
    tokens: bool = False
    requests: bool = False
    model_breakdown: bool = False
    balance_history: bool = False
    usage_history: bool = False


@dataclass(frozen=True)
class ProviderDefinition:
    id: str
    name: str
    company: str
    description: str

    env_keys: tuple[str, ...] = field(
        default_factory=tuple
    )

    capabilities: ProviderCapabilities = field(
        default_factory=ProviderCapabilities
    )

    template: bool = True
    documentation_url: str | None = None


@dataclass
class ProviderState:
    id: str
    name: str

    configured: bool = False
    connected: bool = False

    status: str = "not_configured"
    message: str | None = None

    balance: float | None = None
    currency: str | None = None

    spend: float | None = None
    requests: int | None = None

    input_tokens: int | None = None
    output_tokens: int | None = None
    reasoning_tokens: int | None = None
    cached_tokens: int | None = None
    total_tokens: int | None = None

    extra: dict[str, Any] = field(
        default_factory=dict
    )
