"""Abstract backend contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from jc_speedtest.models import SpeedtestResult


class SpeedtestBackend(ABC):
    """Contract every measurement backend must implement."""

    name: str

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this backend can be used in the current environment."""

    @abstractmethod
    def measure(
        self,
        *,
        download: bool = True,
        upload: bool = True,
        timeout: float = 10.0,
    ) -> SpeedtestResult:
        """Run a full measurement and return an immutable result."""
