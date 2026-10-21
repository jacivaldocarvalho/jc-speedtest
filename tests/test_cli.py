"""Tests for the CLI."""

from __future__ import annotations

import json
from unittest.mock import patch

from jc_speedtest.cli import build_parser, format_human, main
from jc_speedtest.exceptions import MeasurementTimeoutError
from jc_speedtest.models import SpeedtestResult


def _sample() -> SpeedtestResult:
    return SpeedtestResult(
        download_mbps=100.0,
        upload_mbps=50.0,
        ping_ms=15.5,
        backend="native",
        server="https://speed.cloudflare.com",
    )


def test_parser_defaults() -> None:
    args = build_parser().parse_args([])
    assert args.download is True
    assert args.upload is True
    assert args.timeout == 10.0
    assert args.backend == "auto"
    assert args.json_output is False


def test_parser_flags() -> None:
    args = build_parser().parse_args(
        ["--no-download", "--no-upload", "--timeout", "5", "--json", "--backend", "native"]
    )
    assert args.download is False
    assert args.upload is False
    assert args.timeout == 5.0
    assert args.json_output is True
    assert args.backend == "native"


def test_format_human_full() -> None:
    text = format_human(_sample())
    assert "Download: 100.00 Mbps" in text
    assert "Upload  : 50.00 Mbps" in text
    assert "Latency : 15.50 ms" in text


def test_format_human_skipped() -> None:
    result = SpeedtestResult(
        download_mbps=None,
        upload_mbps=None,
        ping_ms=10.0,
        backend="native",
        server=None,
    )
    text = format_human(result)
    assert "Download: skipped" in text
    assert "Upload  : skipped" in text


def test_main_human_output(capsys) -> None:
    with patch("jc_speedtest.cli.run_speedtest", return_value=_sample()):
        code = main([])
    out = capsys.readouterr().out
    assert code == 0
    assert "Download: 100.00 Mbps" in out


def test_main_json_output(capsys) -> None:
    with patch("jc_speedtest.cli.run_speedtest", return_value=_sample()):
        code = main(["--json"])
    out = capsys.readouterr().out
    assert code == 0
    data = json.loads(out)
    assert data["download_mbps"] == 100.0
    assert data["backend"] == "native"
    assert "timestamp" in data


def test_main_handles_error(capsys) -> None:
    with patch("jc_speedtest.cli.run_speedtest", side_effect=MeasurementTimeoutError("boom")):
        code = main([])
    err = capsys.readouterr().err
    assert code == 1
    assert "error: boom" in err
