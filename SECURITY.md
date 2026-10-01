# Security Policy

AI API Cost Dashboard interacts with sensitive API credentials and billing information.

## Secrets

Never commit:

- `.env`
- API keys
- management keys
- access tokens
- private account information
- runtime databases

Use `.env.example` only for environment variable names and empty placeholders.

## Network Exposure

The default Docker configuration binds the application to:

```text
127.0.0.1:8000
