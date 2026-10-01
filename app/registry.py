import os

from app.providers.base import (
    ProviderCapabilities,
    ProviderDefinition,
)


PROVIDERS: tuple[ProviderDefinition, ...] = (

    ProviderDefinition(
        id="openrouter",
        name="OpenRouter",
        company="OpenRouter",
        description=(
            "Multi-model AI API gateway with "
            "usage and analytics support."
        ),
        env_keys=(
            "OPENROUTER_API_KEY",
            "OPENROUTER_MANAGEMENT_KEY",
        ),
        capabilities=ProviderCapabilities(
            balance=True,
            cost=True,
            tokens=True,
            requests=True,
            model_breakdown=True,
            balance_history=True,
            usage_history=True,
        ),
        template=False,
        documentation_url=(
            "https://openrouter.ai/docs"
        ),
    ),

    ProviderDefinition(
        id="deepseek",
        name="DeepSeek",
        company="DeepSeek",
        description=(
            "Direct DeepSeek API integration "
            "with account balance monitoring."
        ),
        env_keys=(
            "DEEPSEEK_API_KEY",
        ),
        capabilities=ProviderCapabilities(
            balance=True,
            balance_history=True,
        ),
        template=False,
        documentation_url=(
            "https://api-docs.deepseek.com/"
        ),
    ),

    ProviderDefinition(
        id="openai",
        name="OpenAI",
        company="OpenAI",
        description=(
            "OpenAI API usage, cost, token, "
            "and request analytics."
        ),
        env_keys=(
            "OPENAI_ADMIN_KEY",
        ),
        capabilities=ProviderCapabilities(
            cost=True,
            tokens=True,
            requests=True,
            model_breakdown=True,
            usage_history=True,
        ),
        template=True,
        documentation_url=(
            "https://platform.openai.com/docs"
        ),
    ),

    ProviderDefinition(
        id="anthropic",
        name="Anthropic",
        company="Anthropic",
        description=(
            "Claude API organization usage "
            "and cost analytics."
        ),
        env_keys=(
            "ANTHROPIC_ADMIN_KEY",
        ),
        capabilities=ProviderCapabilities(
            cost=True,
            tokens=True,
            requests=True,
            model_breakdown=True,
            usage_history=True,
        ),
        template=True,
        documentation_url=(
            "https://docs.anthropic.com/"
        ),
    ),

    ProviderDefinition(
        id="gemini",
        name="Google Gemini",
        company="Google",
        description=(
            "Gemini API integration with "
            "Google Cloud billing support."
        ),
        env_keys=(
            "GEMINI_API_KEY",
        ),
        capabilities=ProviderCapabilities(
            tokens=True,
            requests=True,
        ),
        template=True,
        documentation_url=(
            "https://ai.google.dev/"
        ),
    ),

    ProviderDefinition(
        id="xai",
        name="xAI",
        company="xAI",
        description=(
            "Grok API usage and billing "
            "integration."
        ),
        env_keys=(
            "XAI_MANAGEMENT_API_KEY",
        ),
        capabilities=ProviderCapabilities(
            balance=True,
            cost=True,
            tokens=True,
            requests=True,
            model_breakdown=True,
            balance_history=True,
            usage_history=True,
        ),
        template=True,
        documentation_url=(
            "https://docs.x.ai/"
        ),
    ),

    ProviderDefinition(
        id="mistral",
        name="Mistral AI",
        company="Mistral AI",
        description=(
            "Mistral organization usage "
            "and billing analytics."
        ),
        env_keys=(
            "MISTRAL_ADMIN_API_KEY",
        ),
        capabilities=ProviderCapabilities(
            cost=True,
            tokens=True,
            requests=True,
            model_breakdown=True,
            usage_history=True,
        ),
        template=True,
        documentation_url=(
            "https://docs.mistral.ai/"
        ),
    ),

    ProviderDefinition(
        id="generic",
        name="Generic OpenAI-Compatible",
        company="Custom",
        description=(
            "Template for OpenAI-compatible "
            "API providers."
        ),
        env_keys=(
            "GENERIC_API_KEY",
            "GENERIC_BASE_URL",
        ),
        capabilities=ProviderCapabilities(),
        template=True,
        documentation_url=None,
    ),
)


def get_providers() -> tuple[ProviderDefinition, ...]:
    return PROVIDERS


def get_provider(
    provider_id: str,
) -> ProviderDefinition | None:

    return next(
        (
            provider
            for provider in PROVIDERS
            if provider.id == provider_id
        ),
        None,
    )


def is_provider_configured(
    provider: ProviderDefinition,
) -> bool:

    if not provider.env_keys:
        return False

    return all(
        bool(
            os.getenv(key)
        )
        for key in provider.env_keys
    )


def provider_registry_summary() -> list[dict]:

    result = []

    for provider in PROVIDERS:

        result.append(
            {
                "id": provider.id,
                "name": provider.name,
                "company": provider.company,
                "description": provider.description,
                "configured": (
                    is_provider_configured(
                        provider
                    )
                ),
                "template": provider.template,
                "capabilities": {
                    "balance": (
                        provider.capabilities.balance
                    ),
                    "cost": (
                        provider.capabilities.cost
                    ),
                    "tokens": (
                        provider.capabilities.tokens
                    ),
                    "requests": (
                        provider.capabilities.requests
                    ),
                    "model_breakdown": (
                        provider.capabilities.model_breakdown
                    ),
                    "balance_history": (
                        provider.capabilities.balance_history
                    ),
                    "usage_history": (
                        provider.capabilities.usage_history
                    ),
                },
            }
        )

    return result
