"""HTTP endpoint health check."""

import time
import httpx
from . import BaseCheck, HealthResult


class HttpCheck(BaseCheck):
    type = "http"

    async def check(self, service_config: dict, client_name: str) -> HealthResult:
        url = service_config.get("url", "")
        method = service_config.get("method", "GET").upper()
        timeout = service_config.get("timeout", 10)
        expected_status = service_config.get("expected_status", 200)
        headers = service_config.get("headers", {})

        # Sanitize output — mask auth headers
        sanitized_headers = {}
        for k, v in headers.items():
            sanitized_headers[k] = v if "***" not in str(v) else "***"

        start = time.time()
        try:
            async with httpx.AsyncClient(timeout=timeout, verify=False) as client:
                resp = await client.request(method, url, headers=headers)
            elapsed = (time.time() - start) * 1000

            if resp.status_code == expected_status:
                status = "ok" if elapsed < 1000 else "slow"
                detail = f"HTTP {resp.status_code} in {elapsed:.0f}ms"
                return HealthResult(
                    service=service_config.get("name", url),
                    client=client_name,
                    status=status,
                    latency_ms=elapsed,
                    detail=detail,
                )
            else:
                return HealthResult(
                    service=service_config.get("name", url),
                    client=client_name,
                    status="fail",
                    latency_ms=elapsed,
                    detail=f"Expected HTTP {expected_status}, got {resp.status_code}",
                    error=f"HTTP {resp.status_code}",
                )
        except httpx.TimeoutException:
            elapsed = (time.time() - start) * 1000
            return HealthResult(
                service=service_config.get("name", url),
                client=client_name,
                status="fail",
                latency_ms=elapsed,
                detail=f"Timeout after {timeout}s",
                error="timeout",
            )
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return HealthResult(
                service=service_config.get("name", url),
                client=client_name,
                status="fail",
                latency_ms=elapsed,
                detail=str(e)[:100],
                error=str(e)[:100],
            )
