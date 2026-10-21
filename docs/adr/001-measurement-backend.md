# ADR 001: Measurement Backend Strategy

## Status
Accepted

## Context
We need to measure internet speed (latency, download, upload) without a browser.
Two approaches exist:
1. Pure Python using public HTTP endpoints (e.g., Cloudflare)
2. Delegating to established tools like `speedtest-cli` or Ookla's binary

## Decision
Use a **hybrid approach**:
- **Default**: Native measurement using Cloudflare's speed test endpoints
- **Optional**: If `speedtest-cli` is installed, delegate to it for improved accuracy

The `speedtest-cli` dependency is **optional**, exposed as `jc-speedtest[speedtest]`.

## Consequences
- Package remains lightweight by default (only `httpx`)
- Users needing maximum accuracy on gigabit+ connections can opt-in
- Upload measurement in native mode may be less accurate than dedicated tools
- Clear documentation required about the trade-off
