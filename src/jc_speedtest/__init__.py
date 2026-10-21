"""jc-speedtest: lightweight internet speed test for Python."""

from jc_speedtest.core import run_speedtest
from jc_speedtest.exceptions import (
    JCSpeedtestError,
    MeasurementFailedError,
    MeasurementTimeoutError,
    NoBackendAvailableError,
)
from jc_speedtest.models import SpeedtestResult

__version__ = "0.1.0"

__all__ = [
    "JCSpeedtestError",
    "MeasurementFailedError",
    "MeasurementTimeoutError",
    "NoBackendAvailableError",
    "SpeedtestResult",
    "__version__",
    "run_speedtest",
]