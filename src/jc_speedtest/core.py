"""Orchestration layer: choose backend and run measurement."""

from __future__ import annotations

import warnings
from typing import Literal

from jc_speedtest.backends import (
    NativeBackend,
    SpeedtestBackend,
    SpeedtestCliBackend,
)
from jc_speedtest.models import SpeedtestResult

BackendPreference = Literal["auto", "native", "speedtest-cli"]


def _resolve_backend(preference: BackendPreference) -> SpeedtestBackend:
    candidates: list[SpeedtestBackend]
    if preference == "native":
        candidates = [NativeBackend()]
    elif preference == "speedtest-cli":
        candidates = [SpeedtestCliBackend()]
    else:  # auto
        candidates = [SpeedtestCliBackend(), NativeBackend()]

    for backend in candidates:
        if backend.is_available():
            return backend

    # Defensive: NativeBackend.is_available() always returns True.
    warnings.warn(
        "No preferred backend available; falling back to native.",
        stacklevel=2,
    )
    return NativeBackend()


def run_speedtest(
    *,
    download: bool = True,
    upload: bool = True,
    timeout: float = 10.0,
    backend: BackendPreference = "auto",
) -> SpeedtestResult:
    """Run an internet speed test and return an immutable result.

    Args:
        download: Whether to measure download speed.
        upload: Whether to measure upload speed.
        timeout: Per-phase timeout in seconds.
        backend: "auto" prefers speedtest-cli if installed, else native.

    Returns:
        A SpeedtestResult instance.

    Raises:
        MeasurementTimeoutError: If a phase exceeds the timeout.
        MeasurementFailedError: If a phase fails for any other reason.

    Warns:
        UserWarning: If the requested backend is unavailable and a fallback
            is used.
    """
    selected = _resolve_backend(backend)
    return selected.measure(download=download, upload=upload, timeout=timeout)
