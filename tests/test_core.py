"""Tests for the core orchestration layer."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from jc_speedtest.backends import NativeBackend, SpeedtestCliBackend
from jc_speedtest.core import _resolve_backend, run_speedtest
from jc_speedtest.models import SpeedtestResult


def test_run_speedtest_auto_prefers_native() -> None:
    # O padrão "auto" agora prefere o native.
    with (
        patch.object(SpeedtestCliBackend, "is_available", return_value=True),
        patch.object(NativeBackend, "measure") as mock_measure_native,
    ):
        mock_measure_native.return_value = SpeedtestResult(
            download_mbps=80.0,
            upload_mbps=40.0,
            ping_ms=12.0,
            backend="native",
        )
        result = run_speedtest(backend="auto")

        assert result.backend == "native"
        mock_measure_native.assert_called_once()


def test_run_speedtest_auto_falls_back_to_native() -> None:
    with (
        patch.object(SpeedtestCliBackend, "is_available", return_value=False),
        patch.object(NativeBackend, "measure") as mock_measure,
    ):
        mock_measure.return_value = SpeedtestResult(
            download_mbps=80.0,
            upload_mbps=40.0,
            ping_ms=12.0,
            backend="native",
        )
        result = run_speedtest(backend="auto")
        assert result.backend == "native"


def test_run_speedtest_explicit_speedtest_cli_works() -> None:
    # Se o usuário forçar o speedtest-cli, ele deve ser usado.
    with (
        patch.object(SpeedtestCliBackend, "is_available", return_value=True),
        patch.object(SpeedtestCliBackend, "measure") as mock_measure_cli,
    ):
        mock_measure_cli.return_value = SpeedtestResult(
            download_mbps=100.0,
            upload_mbps=50.0,
            ping_ms=10.0,
            backend="speedtest-cli",
        )
        result = run_speedtest(backend="speedtest-cli")

        assert result.backend == "speedtest-cli"
        mock_measure_cli.assert_called_once()


def test_resolve_backend_warns_when_nothing_available() -> None:
    with (
        patch.object(SpeedtestCliBackend, "is_available", return_value=False),
        patch.object(NativeBackend, "is_available", return_value=False),
        pytest.warns(UserWarning, match="falling back to native"),
    ):
        backend = _resolve_backend("speedtest-cli")
    assert isinstance(backend, NativeBackend)
