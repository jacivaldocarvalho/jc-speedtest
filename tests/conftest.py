"""Shared fixtures for jc-speedtest tests."""

from __future__ import annotations

import pytest

from jc_speedtest.models import SpeedtestResult


@pytest.fixture
def sample_result() -> SpeedtestResult:
    """Provide a representative, immutable speed test result."""
    return SpeedtestResult(
        download_mbps=100.0,
        upload_mbps=50.0,
        ping_ms=15.5,
        backend="native",
        server="https://speed.cloudflare.com",
    )
