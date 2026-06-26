# Safety

## Denylist Paths
- `.env` files, `*.pem`, `*.key`
- `config/clients.yaml` contains placeholder keys only — never commit real API keys

## Escalation
- CI failure 3x in a row on same test → flag human
- Dependency with known CVE → auto-patch patch-level only
- No auto-merge. All PRs reviewed.

## Kill Switch
- `loop-pause-all` in STATE.md → pause all loops
