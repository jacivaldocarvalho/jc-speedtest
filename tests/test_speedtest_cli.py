"""Tests for the optional speedtest-cli backend (mocked)."""

from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock, patch

import pytest

from jc_speedtest.backends.speedtest_cli import SpeedtestCliBackend
from jc_speedtest.exceptions import MeasurementFailedError


def _install_fake_speedtest(
    download: float = 100_000_000,
    upload: float = 50_000_000,
    ping: float = 12.5,
    server_name: str = "MockServer",
) -> types.ModuleType:
    fake = types.ModuleType("speedtest")
    instance = MagicMock()
    instance.download.return_value = download
    instance.upload.return_value = upload
    instance.results.dict.return_value = {
        "ping": ping,
        "server": {"name": server_name},
    }
    fake.Speedtest = MagicMock(return_value=instance)  # type: ignore[attr-defined]
    fake._instance = instance  # type: ignore[attr-defined]
    return fake


def test_is_available_true_when_importable() -> None:
    with patch.dict(sys.modules, {"speedtest": _install_fake_speedtest()}):
        assert SpeedtestCliBackend().is_available() is True


def test_is_available_false_when_missing() -> None:
    from typing import Any  # Adicione no topo do arquivo se preferir

    real_import = __import__

    def fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "speedtest":
            raise ImportError("simulated absence")
        return real_import(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=fake_import):
        assert SpeedtestCliBackend().is_available() is False


def test_measure_full_success() -> None:
    fake = _install_fake_speedtest()
    with patch.dict(sys.modules, {"speedtest": fake}):
        result = SpeedtestCliBackend().measure()

    assert result.backend == "speedtest-cli"
    assert result.download_mbps == pytest.approx(100.0)
    assert result.upload_mbps == pytest.approx(50.0)
    assert result.ping_ms == pytest.approx(12.5)
    assert result.server == "MockServer"


def test_measure_skip_download_and_upload() -> None:
    fake = _install_fake_speedtest()
    with patch.dict(sys.modules, {"speedtest": fake}):
        result = SpeedtestCliBackend().measure(download=False, upload=False)

    assert result.download_mbps is None
    assert result.upload_mbps is None


def test_measure_wraps_exceptions() -> None:
    fake = _install_fake_speedtest()
    instance = fake._instance
    instance.download.side_effect = RuntimeError("boom")

    with (
        patch.dict(sys.modules, {"speedtest": fake}),
        pytest.raises(MeasurementFailedError, match="boom"),
    ):
        SpeedtestCliBackend().measure()
