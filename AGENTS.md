# AGENTS.md — smb-automation-health

## Quick commands

```bash
python3 app.py                          # start server on :8080
python3 -m pytest tests/ -v              # run test suite
python3 -m checks.runner                # dry-run health checks in terminal
```

## Stack

Flask + httpx + pytest + GitHub Actions CI

## Config

Edit `config/clients.yaml`. API keys via env vars (see README).

## Loop state

See `STATE.md` for daily triage output. Run log in `loop-run-log.md`.
