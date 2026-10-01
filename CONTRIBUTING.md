# Contributing

Thank you for contributing to AI API Cost Dashboard.

## Development Setup

Clone the repository:

```bash
git clone https://github.com/acengkemoceng/api-cost-dashboard.git
cd api-cost-dashboard
```

Create local configuration:

```bash
cp .env.example .env
```

For development without real provider credentials:

```env
DEMO_MODE=true
```

Build:

```bash
docker compose up -d --build
```

Check application health:

```bash
curl http://127.0.0.1:8000/health
```

## Contribution Guidelines

Contributions should:

- keep provider credentials server-side
- never commit secrets
- avoid fabricating unsupported metrics
- preserve Demo Mode
- preserve responsive behavior
- gracefully handle unavailable provider APIs
- update documentation when behavior changes
- keep provider capability declarations accurate

## Provider Adapters

Provider integrations should expose only metrics that can be retrieved reliably.

Unsupported values should not be represented as `0`.

Prefer:

- `None`
- an unavailable capability
- an explicit unsupported state

instead of fabricated data.

## Testing

Before submitting changes:

```bash
docker compose up -d --build
```

Check:

```bash
curl http://127.0.0.1:8000/health
```

Also test Demo Mode:

```env
DEMO_MODE=true
```

When provider credentials are available, test Live Mode:

```env
DEMO_MODE=false
```

## Commit Style

Suggested commit prefixes:

```text
feat:
fix:
docs:
refactor:
test:
chore:
```

Examples:

```text
feat: add OpenAI usage adapter
fix: handle missing DeepSeek balance
docs: improve Docker setup
refactor: simplify provider registry
test: add provider adapter tests
chore: update dependencies
```
