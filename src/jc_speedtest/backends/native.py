"""Native backend using Cloudflare's public speed test endpoints."""

from __future__ import annotations

import os
import statistics
import time

import httpx

from jc_speedtest.backends.base import SpeedtestBackend
from jc_speedtest.exceptions import MeasurementFailedError, MeasurementTimeoutError
from jc_speedtest.models import SpeedtestResult

DEFAULT_BASE_URL = "https://speed.cloudflare.com"
LATENCY_SAMPLES = 5
DOWNLOAD_BYTES = 25_000_000  # 25 MB
UPLOAD_BYTES = 10_000_000  # 10 MB


class NativeBackend(SpeedtestBackend):
    """Measure speed using plain HTTP against Cloudflare's endpoints."""

    name = "native"

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (
            base_url
            or os.getenv("JC_SPEEDTEST_BASE_URL")
            or DEFAULT_BASE_URL
        ).rstrip("/")

    def is_available(self) -> bool:
        return True

    def measure(
        self,
        *,
        download: bool = True,
        upload: bool = True,
        timeout: float = 10.0,
    ) -> SpeedtestResult:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            ping_ms = self._measure_latency(client)
            download_mbps = self._measure_download(client) if download else None
            upload_mbps = self._measure_upload(client) if upload else None

        return SpeedtestResult(
            download_mbps=download_mbps,
            upload_mbps=upload_mbps,
            ping_ms=ping_ms,
            backend="native",
            server=self.base_url,
        )

    def _measure_latency(self, client: httpx.Client) -> float:
        samples: list[float] = []
        for _ in range(LATENCY_SAMPLES):
            try:
                start = time.perf_counter()
                client.get(f"{self.base_url}/__down", params={"bytes": 0})
                samples.append((time.perf_counter() - start) * 1000)
            except httpx.TimeoutException as exc:
                raise MeasurementTimeoutError("latency probe timed out") from exc
            except httpx.HTTPError as exc:
                raise MeasurementFailedError(f"latency probe failed: {exc}") from exc
        return statistics.median(samples)

    def _measure_download(self, client: httpx.Client) -> float:
        try:
            start = time.perf_counter()
            with client.stream(
                "GET", f"{self.base_url}/__down", params={"bytes": DOWNLOAD_BYTES}
            ) as response:
                response.raise_for_status()
                total = sum(len(chunk) for chunk in response.iter_bytes())
            elapsed = time.perf_counter() - start
        except httpx.TimeoutException as exc:
            raise MeasurementTimeoutError("download measurement timed out") from exc
        except httpx.HTTPError as exc:
            raise MeasurementFailedError(f"download measurement failed: {exc}") from exc

        if elapsed <= 0:
            raise MeasurementFailedError("invalid elapsed time for download")
        return (total * 8) / elapsed / 1_000_000

    def _measure_upload(self, client: httpx.Client) -> float:
        payload = b"\x00" * UPLOAD_BYTES
        try:
            start = time.perf_counter()
            response = client.post(f"{self.base_url}/__up", content=payload)
            response.raise_for_status()
            elapsed = time.perf_counter() - start
        except httpx.TimeoutException as exc:
            raise MeasurementTimeoutError("upload measurement timed out") from exc
        except httpx.HTTPError as exc:
            raise MeasurementFailedError(f"upload measurement failed: {exc}") from exc

        if elapsed <= 0:
            raise MeasurementFailedError("invalid elapsed time for upload")
        return (len(payload) * 8) / elapsed / 1_000_000