"""Tests for the result model."""

from __future__ import annotations

from jc_speedtest.models import SpeedtestResult


def test_to_dict_is_json_friendly(sample_result: SpeedtestResult) -> None:
    data = sample_result.to_dict()
    assert data["download_mbps"] == 100.0
    assert data["backend"] == "native"
    assert isinstance(data["timestamp"], str)


def test_result_is_immutable(sample_result: SpeedtestResult) -> None:
    import dataclasses
    assert dataclasses.is_dataclass(sample_result)
    try:
        sample_result.download_mbps = 1.0  # type: ignore[misc]
    except dataclasses.FrozenInstanceError:
        return
    raise AssertionError("SpeedtestResult should be frozen")