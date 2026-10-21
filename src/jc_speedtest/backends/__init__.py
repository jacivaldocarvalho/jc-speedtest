"""Backends available in jc-speedtest."""

from jc_speedtest.backends.base import SpeedtestBackend
from jc_speedtest.backends.native import NativeBackend
from jc_speedtest.backends.speedtest_cli import SpeedtestCliBackend

__all__ = ["NativeBackend", "SpeedtestBackend", "SpeedtestCliBackend"]
