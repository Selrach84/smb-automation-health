"""Tests for smb-automation-health check modules."""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from checks.http_check import HttpCheck
from checks.ghl_check import GhlCheck
from checks import HealthResult


class TestHealthResult:
    def test_to_dict(self):
        r = HealthResult(service="Test", client="Client", status="ok", latency_ms=100.0, detail="OK")
        d = r.to_dict()
        assert d["service"] == "Test"
        assert d["status"] == "ok"
        assert d["latency_ms"] == 100.0

    def test_error_optional(self):
        r = HealthResult(service="S", client="C", status="fail", latency_ms=0, detail="err", error="timeout")
        assert r.error == "timeout"

    def test_no_error(self):
        r = HealthResult(service="S", client="C", status="ok", latency_ms=50.0, detail="fine")
        assert r.error is None


class TestHttpCheck:
    @pytest.mark.asyncio
    async def test_http_check_real(self):
        """Hit a real public API endpoint to verify the checker works."""
        check = HttpCheck()
        result = await check.check(
            {
                "name": "GitHub API",
                "type": "http",
                "url": "https://api.github.com",
                "method": "GET",
                "timeout": 10,
                "expected_status": 200,
            },
            "TestClient",
        )
        assert result.status in ("ok", "slow")
        assert result.latency_ms > 0
        assert result.latency_ms < 10000  # sanity: under 10s

    @pytest.mark.asyncio
    async def test_http_check_timeout(self):
        """Point at a non-routable address to trigger timeout."""
        check = HttpCheck()
        result = await check.check(
            {
                "name": "Timeout Test",
                "type": "http",
                "url": "http://10.255.255.1:1",
                "method": "GET",
                "timeout": 2,
                "expected_status": 200,
            },
            "TestClient",
        )
        assert result.status == "fail"

    @pytest.mark.asyncio
    async def test_http_check_non_200(self):
        """Verify non-200 status is reported as fail."""
        check = HttpCheck()
        result = await check.check(
            {
                "name": "Non-200 Test",
                "type": "http",
                "url": "https://httpbin.org/status/418",
                "method": "GET",
                "timeout": 10,
                "expected_status": 200,
            },
            "TestClient",
        )
        assert result.status == "fail"
        assert result.error is not None


class TestGhlCheck:
    @pytest.mark.asyncio
    async def test_ghl_bad_key(self):
        """Bad API key should return auth_failed."""
        check = GhlCheck()
        result = await check.check(
            {
                "name": "GHL Test",
                "type": "ghl",
                "api_key": "bad-key-12345",
                "sub_account": "test",
                "timeout": 10,
            },
            "TestClient",
        )
        assert result.status == "fail"

    @pytest.mark.asyncio
    async def test_ghl_missing_key(self):
        """Missing API key should fail fast."""
        check = GhlCheck()
        result = await check.check(
            {
                "name": "GHL Test",
                "type": "ghl",
                "api_key": "",
                "sub_account": "test",
                "timeout": 10,
            },
            "TestClient",
        )
        assert result.status == "fail"
        assert "missing" in result.error.lower()


class TestRunner:
    def test_runner_imports(self):
        from checks.runner import run_checks_sync, run_checks
        assert callable(run_checks_sync)
        assert callable(run_checks)

    def test_runner_empty_config(self):
        from checks.runner import run_checks_sync
        results = run_checks_sync({"clients": []})
        assert results == []

    def test_runner_empty_services(self):
        from checks.runner import run_checks_sync
        results = run_checks_sync({"clients": [{"name": "Empty", "services": []}]})
        assert len(results) == 0
