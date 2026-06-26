"""Health check runner — dispatches checks by type."""

import asyncio
from typing import List
from . import HealthResult, BaseCheck
from .http_check import HttpCheck
from .ghl_check import GhlCheck

# Registry of check types
CHECK_REGISTRY: dict[str, BaseCheck] = {}
for cls in [HttpCheck, GhlCheck]:
    CHECK_REGISTRY[cls.type] = cls()


async def run_checks(config: dict) -> List[HealthResult]:
    """Run all health checks for all clients in parallel."""
    tasks = []
    clients = config.get("clients", [])

    for client in clients:
        client_name = client.get("name", "Unknown")
        for service in client.get("services", []):
            check_type = service.get("type", "http")
            checker = CHECK_REGISTRY.get(check_type)
            if checker:
                tasks.append(checker.check(service, client_name))

    if not tasks:
        return []

    results = await asyncio.gather(*tasks, return_exceptions=True)

    final = []
    for r in results:
        if isinstance(r, Exception):
            final.append(HealthResult(
                service="unknown",
                client="unknown",
                status="fail",
                latency_ms=0,
                detail=str(r)[:100],
                error="check_error",
            ))
        else:
            final.append(r)

    return final


def run_checks_sync(config: dict) -> List[dict]:
    """Synchronous wrapper for Flask routes."""
    results = asyncio.run(run_checks(config))
    return [r.to_dict() for r in sorted(results, key=lambda x: (x.status, x.client, x.service))]
