# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-22

### Added
- Native backend using Cloudflare public endpoints for latency, download, and upload measurement.
- Optional `speedtest-cli` backend, installable via `jc-speedtest[speedtest]`.
- `run_speedtest()` public API returning an immutable `SpeedtestResult`.
- `jc-speedtest` CLI with `--json`, `--no-download`, `--no-upload`, `--timeout`, and `--backend` flags.
- `python -m jc_speedtest` execution support.
- Granular `httpx.Timeout` to avoid false timeouts on slower connections.
- Warm-up request in latency measurement to discard TCP/TLS handshake cost.
- Full test suite (unit + integration) with `pytest`, `ruff`, and `mypy`.

### Changed
- The `auto` backend mode now prioritizes the native backend for speed and zero configuration. The `speedtest-cli` backend must be explicitly requested or installed.