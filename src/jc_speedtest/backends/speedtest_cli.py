"""Optional backend delegating to speedtest-cli when installed."""

from __future__ import annotations

from typing import Any

from jc_speedtest.backends.base import SpeedtestBackend
from jc_speedtest.exceptions import MeasurementFailedError
from jc_speedtest.models import SpeedtestResult


class SpeedtestCliBackend(SpeedtestBackend):
    """Delegate measurement to the `speedtest-cli` package if importable.

    Note:
        The ``timeout`` argument is accepted for interface symmetry but is
        **not honored**, because ``speedtest-cli`` manages its own internal
        timeouts. Callers relying on strict time bounds should prefer the
        native backend.
    """

    name = "speedtest-cli"

    def is_available(self) -> bool:
        try:
            import speedtest  # noqa: F401
        except ImportError:
            return False
        return True

    def measure(
        self,
        *,
        download: bool = True,
        upload: bool = True,
        timeout: float = 10.0,  # noqa: ARG002 - documented limitation
    ) -> SpeedtestResult:
        import speedtest

        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            download_mbps = st.download() / 1_000_000 if download else None
            upload_mbps = st.upload() / 1_000_000 if upload else None
            results: dict[str, Any] = st.results.dict()
        except Exception as exc:  # speedtest-cli raises broad exceptions
            raise MeasurementFailedError(f"speedtest-cli failed: {exc}") from exc

        return SpeedtestResult(
            download_mbps=download_mbps,
            upload_mbps=upload_mbps,
            ping_ms=results.get("ping"),
            backend="speedtest-cli",
            server=results.get("server", {}).get("name"),
        )