"""GoHighLevel API health check."""

import time
import httpx
from . import BaseCheck, HealthResult


class GhlCheck(BaseCheck):
    type = "ghl"

    async def check(self, service_config: dict, client_name: str) -> HealthResult:
        api_key = service_config.get("api_key", "")
        sub_account = service_config.get("sub_account", "")
        timeout = service_config.get("timeout", 10)

        if not api_key or api_key == "":
            return HealthResult(
                service=service_config.get("name", "GoHighLevel"),
                client=client_name,
                status="fail",
                latency_ms=0,
                detail="No API key configured",
                error="missing_api_key",
            )

        start = time.time()
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(
                    "https://rest.gohighlevel.com/v1/ping/",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                )
            elapsed = (time.time() - start) * 1000

            if resp.status_code == 200:
                # Also check quota
                quota_remaining = resp.headers.get("X-RateLimit-Remaining", "?")
                status = "ok" if elapsed < 1500 else "slow"
                return HealthResult(
                    service=service_config.get("name", "GoHighLevel"),
                    client=client_name,
                    status=status,
                    latency_ms=elapsed,
                    detail=f"API OK — {quota_remaining} req remaining",
                )
            elif resp.status_code == 401:
                return HealthResult(
                    service=service_config.get("name", "GoHighLevel"),
                    client=client_name,
                    status="fail",
                    latency_ms=elapsed,
                    detail="Invalid API key (401)",
                    error="auth_failed",
                )
            elif resp.status_code == 429:
                return HealthResult(
                    service=service_config.get("name", "GoHighLevel"),
                    client=client_name,
                    status="fail",
                    latency_ms=elapsed,
                    detail="Rate limited (429)",
                    error="rate_limited",
                )
            else:
                return HealthResult(
                    service=service_config.get("name", "GoHighLevel"),
                    client=client_name,
                    status="fail",
                    latency_ms=elapsed,
                    detail=f"HTTP {resp.status_code}",
                    error=f"http_{resp.status_code}",
                )
        except httpx.TimeoutException:
            elapsed = (time.time() - start) * 1000
            return HealthResult(
                service=service_config.get("name", "GoHighLevel"),
                client=client_name,
                status="fail",
                latency_ms=elapsed,
                detail=f"Timeout after {timeout}s",
                error="timeout",
            )
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return HealthResult(
                service=service_config.get("name", "GoHighLevel"),
                client=client_name,
                status="fail",
                latency_ms=elapsed,
                detail=str(e)[:100],
                error=str(e)[:100],
            )
