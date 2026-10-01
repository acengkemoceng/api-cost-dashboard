# AI API Cost Dashboard

A self-hosted dashboard for monitoring AI API balances, spending, requests, token usage, historical usage, and provider integrations.

Built with FastAPI, SQLite, Docker, Jinja2, and Chart.js.

> AI providers expose different billing and usage APIs. This project only displays metrics that can be retrieved reliably and does not fabricate unsupported values.

## Features

- Unified multi-provider overview
- API balance monitoring
- Spending analytics
- Request tracking
- Token usage analytics
- Input/output/reasoning/cache token breakdown
- Average cost per request
- Average cost per 1K tokens
- Model usage breakdown
- Historical usage charts
- Historical balance charts
- Background snapshot collector
- Provider capability registry
- Responsive interface
- Docker deployment
- Demo mode
- No local LLM required

## Provider Support

| Provider | Status | Balance | Cost | Tokens | Requests | Models |
|---|---|---:|---:|---:|---:|---:|
| OpenRouter | Implemented | ✅ | ✅ | ✅ | ✅ | ✅ |
| DeepSeek | Implemented | ✅ | Limited | Limited | Limited | — |
| OpenAI | Template | — | Planned | Planned | Planned | Planned |
| Anthropic | Template | — | Planned | Planned | Planned | Planned |
| Google Gemini | Template | Planned | Planned | Planned | Planned | Planned |
| xAI | Template | Planned | Planned | Planned | Planned | Planned |
| Mistral AI | Template | Planned | Planned | Planned | Planned | Planned |
| Generic OpenAI-Compatible | Template | Provider dependent | Provider dependent | Provider dependent | Provider dependent | Provider dependent |

`Limited` means that the provider currently does not expose the same account-wide telemetry used by a fully supported integration.

## Dashboard

The interface contains four primary views:

- **Overview** — unified balances and tracked telemetry
- **OpenRouter** — billing, requests, tokens, models, and usage history
- **DeepSeek** — balance and balance history
- **Integrations** — provider registry and supported capabilities

## Architecture

```mermaid
flowchart TD
    Browser[Web Browser]

    Browser --> API[FastAPI Dashboard]

    API --> Registry[Provider Registry]
    API --> DB[(SQLite)]

    Registry --> OR[OpenRouter Adapter]
    Registry --> DS[DeepSeek Adapter]
    Registry --> Templates[Provider Templates]

    OR --> ORAPI[OpenRouter API]
    DS --> DSAPI[DeepSeek API]

    Collector[Background Collector]
    Collector --> OR
    Collector --> DS
    Collector --> DB

    DB --> Charts[Chart.js]
    Charts --> Browser
