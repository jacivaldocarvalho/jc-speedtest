"""Tests for python -m jc_speedtest."""

from __future__ import annotations

import subprocess
import sys


def test_module_help_runs() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "jc_speedtest", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "jc-speedtest" in result.stdout
    assert "--backend" in result.stdout


def test_module_version_runs() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "jc_speedtest", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "0.1.0" in result.stdout
