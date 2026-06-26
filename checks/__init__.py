"""Base health check interface."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class HealthResult:
    service: str
    client: str
    status: str  # "ok" | "slow" | "fail"
    latency_ms: float
    detail: str = ""
    error: Optional[str] = None

    def to_dict(self):
        return {
            "service": self.service,
            "client": self.client,
            "status": self.status,
            "latency_ms": round(self.latency_ms, 1),
            "detail": self.detail,
            "error": self.error,
        }


class BaseCheck:
    type: str = ""

    async def check(self, service_config: dict, client_name: str) -> HealthResult:
        raise NotImplementedError
