"""Tests for the native backend using httpx.MockTransport."""

from __future__ import annotations

from collections.abc import Callable, Iterable

import httpx
import pytest

from jc_speedtest.backends.native import (
    NativeBackend,
)
from jc_speedtest.exceptions import MeasurementFailedError, MeasurementTimeoutError

BASE = "https://speed.cloudflare.com"


def _make_client(handler: Callable[[httpx.Request], httpx.Response]) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler), timeout=10.0)


def _factory(handler: Callable[[httpx.Request], httpx.Response]) -> Callable[..., httpx.Client]:
    def make(**_: object) -> httpx.Client:
        return _make_client(handler)

    return make


def _fake_time(values: Iterable[float]) -> Callable[[], float]:
    it = iter(values)

    def fake() -> float:
        return next(it)

    return fake


def test_measure_full_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/__down":
            size = int(request.url.params.get("bytes", "0"))
            if size == 0:
                return httpx.Response(200, content=b"")
            return httpx.Response(200, content=b"\x00" * size)
        if request.url.path == "/__up":
            return httpx.Response(200, content=b"")
        return httpx.Response(404)

    backend = NativeBackend(base_url=BASE, client_factory=_factory(handler))
    result = backend.measure()

    assert result.backend == "native"
    assert result.ping_ms is not None and result.ping_ms >= 0
    assert result.download_mbps is not None and result.download_mbps > 0
    assert result.upload_mbps is not None and result.upload_mbps > 0


def test_measure_latency_timeout_raises() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("boom")

    backend = NativeBackend(base_url=BASE, client_factory=_factory(handler))
    with pytest.raises(MeasurementTimeoutError):
        backend._measure_latency(_make_client(handler))


def test_measure_latency_http_error_raises() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.HTTPError("kaboom")

    backend = NativeBackend(base_url=BASE, client_factory=_factory(handler))
    with pytest.raises(MeasurementFailedError):
        backend._measure_latency(_make_client(handler))


def test_measure_download_http_error_raises() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    backend = NativeBackend(base_url=BASE, client_factory=_factory(handler))
    with pytest.raises(MeasurementFailedError):
        backend._measure_download(_make_client(handler))


def test_measure_upload_http_error_raises() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    backend = NativeBackend(base_url=BASE, client_factory=_factory(handler))
    with pytest.raises(MeasurementFailedError):
        backend._measure_upload(_make_client(handler))


def test_measure_download_timeout_raises() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("boom")

    backend = NativeBackend(base_url=BASE, client_factory=_factory(handler))
    with pytest.raises(MeasurementTimeoutError):
        backend._measure_download(_make_client(handler))


def test_measure_upload_timeout_raises() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("boom")

    backend = NativeBackend(base_url=BASE, client_factory=_factory(handler))
    with pytest.raises(MeasurementTimeoutError):
        backend._measure_upload(_make_client(handler))


def test_measure_download_invalid_elapsed_raises() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"\x00" * 1024)

    times = _fake_time([1.0, 1.0])  # start == end -> elapsed == 0
    backend = NativeBackend(
        base_url=BASE,
        client_factory=_factory(handler),
        time_source=times,
    )
    with pytest.raises(MeasurementFailedError):
        backend._measure_download(_make_client(handler))


def test_measure_upload_invalid_elapsed_raises() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"")

    times = _fake_time([1.0, 1.0])
    backend = NativeBackend(
        base_url=BASE,
        client_factory=_factory(handler),
        time_source=times,
    )
    with pytest.raises(MeasurementFailedError):
        backend._measure_upload(_make_client(handler))


def test_skip_download_and_upload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/__down":
            return httpx.Response(200, content=b"")
        return httpx.Response(200, content=b"")

    backend = NativeBackend(base_url=BASE, client_factory=_factory(handler))
    result = backend.measure(download=False, upload=False)
    assert result.download_mbps is None
    assert result.upload_mbps is None
    assert result.ping_ms is not None


def test_latency_uses_median() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"")

    # 5 samples => 10 calls to time_source. Each sample must be 10, 20, 30,
    # 40, 50 ms so that the median is 30.
    times = _fake_time(
        [
            0.0,
            0.010,
            1.0,
            1.020,
            2.0,
            2.030,
            3.0,
            3.040,
            4.0,
            4.050,
        ]
    )
    backend = NativeBackend(
        base_url=BASE,
        client_factory=_factory(handler),
        time_source=times,
    )
    value = backend._measure_latency(_make_client(handler))
    assert value == pytest.approx(30.0)


def test_warmup_timeout_raises() -> None:
    calls = {"n": 0}

    def handler(_request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:  # warm-up
            raise httpx.TimeoutException("boom")
        return httpx.Response(200, content=b"")

    backend = NativeBackend(base_url=BASE, client_factory=_factory(handler))
    with pytest.raises(MeasurementTimeoutError):
        backend._measure_latency(_make_client(handler))


def test_warmup_http_error_raises() -> None:
    calls = {"n": 0}

    def handler(_request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:  # warm-up
            raise httpx.HTTPError("kaboom")
        return httpx.Response(200, content=b"")

    backend = NativeBackend(base_url=BASE, client_factory=_factory(handler))
    with pytest.raises(MeasurementFailedError):
        backend._measure_latency(_make_client(handler))
