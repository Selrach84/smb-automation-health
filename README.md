# smb-automation-health

SaaS health monitor for SMB automation stacks. Checks n8n, GoHighLevel, Stripe, Calendly, and any HTTP endpoint — catches expired API keys, rate limits, and dead webhooks before your clients notice.

```bash
pip install -r requirements.txt
python app.py
# → http://localhost:8080
```

## Dashboard

- **Green** = healthy
- **Yellow** = slow (>1s response)
- **Red** = failing (needs attention)

Auto-refreshes every 30s. Click "Refresh All" for immediate check.

## Config

Edit `config/clients.yaml` to add your clients. API keys via env vars:

```bash
export GHL_JOHN_API_KEY=xxx
export STRIPE_JOHN_SECRET_KEY=xxx
```

## Tests

```bash
pip install pytest pytest-asyncio httpx
pytest -v
```

## License

MIT
