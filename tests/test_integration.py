"""Real network integration tests.

These are skipped by default. Enable with: pytest -m integration
"""

from __future__ import annotations

import pytest

from jc_speedtest.backends.native import NativeBackend

pytestmark = pytest.mark.integration


def test_native_backend_real_measurement() -> None:
    backend = NativeBackend()
    result = backend.measure(download=True, upload=False, timeout=30.0)

    assert result.backend == "native"
    assert result.ping_ms is not None
    assert result.ping_ms > 0
    assert result.download_mbps is not None
    assert result.download_mbps > 0.1  # sanity floor: 100 Kbps
    assert result.upload_mbps is None  # skipped
