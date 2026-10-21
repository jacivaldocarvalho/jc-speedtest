"""Command-line interface for jc-speedtest."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from jc_speedtest import __version__
from jc_speedtest.core import run_speedtest
from jc_speedtest.exceptions import JCSpeedtestError
from jc_speedtest.models import SpeedtestResult


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="jc-speedtest",
        description="Lightweight internet speed test. No browser, no ads.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Emit the result as JSON instead of human-readable text.",
    )
    parser.add_argument(
        "--no-download",
        action="store_false",
        dest="download",
        help="Skip the download measurement.",
    )
    parser.add_argument(
        "--no-upload",
        action="store_false",
        dest="upload",
        help="Skip the upload measurement.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        metavar="SECONDS",
        help="Per-phase timeout in seconds (default: 10).",
    )
    parser.add_argument(
        "--backend",
        choices=("auto", "native", "speedtest-cli"),
        default="auto",
        help="Measurement backend to use (default: auto).",
    )
    return parser


def format_human(result: SpeedtestResult) -> str:
    """Render a result for terminal display."""
    lines = [
        f"Latency : {result.ping_ms:.2f} ms" if result.ping_ms is not None else "Latency : n/a",
        f"Download: {result.download_mbps:.2f} Mbps"
        if result.download_mbps is not None
        else "Download: skipped",
        f"Upload  : {result.upload_mbps:.2f} Mbps"
        if result.upload_mbps is not None
        else "Upload  : skipped",
        f"Backend : {result.backend}",
        f"Server  : {result.server or 'n/a'}",
    ]
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the jc-speedtest command."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = run_speedtest(
            download=args.download,
            upload=args.upload,
            timeout=args.timeout,
            backend=args.backend,
        )
    except JCSpeedtestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json_output:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(format_human(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
