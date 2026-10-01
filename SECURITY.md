# Security Policy

## Secrets

Never commit sensitive credentials such as:

- `.env`
- API keys
- management keys
- access tokens
- private account information
- runtime database files

Use `.env.example` only for variable names and empty placeholders.

## Network Exposure

By default, AI API Cost Dashboard binds to:

```text
127.0.0.1:8000
