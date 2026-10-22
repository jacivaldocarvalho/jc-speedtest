# ADR 001: Measurement Backend Strategy

## Status
Accepted (Updated)

## Context
We need to measure internet speed (latency, download, upload) without a browser.
Two approaches exist:
1. Pure Python using public HTTP endpoints (e.g., Cloudflare).
2. Delegating to established tools like `speedtest-cli` or Ookla's binary.

The tool is intended for use in SRE, DevOps, and Telecom environments where CLI startup time, package size, and zero-configuration execution are critical.

## Decision
Use a **hybrid approach**, but with a clear prioritization to ensure the tool is fast and lightweight out-of-the-box.

- **Native (Default for `--backend auto`)**: The package uses Cloudflare's public endpoints via `httpx` by default. This requires zero external dependencies (beyond `httpx`) and starts immediately.
- **Optional (`--backend speedtest-cli`)**: If the user explicitly wants industry-standard server selection (Ookla network) and installs the extra `jc-speedtest[speedtest]`, the tool can delegate to the `speedtest-cli` package.

The `speedtest-cli` dependency is **strictly optional**. The `auto` mode will **never** automatically select `speedtest-cli` just because it is installed in the environment. It must be explicitly requested by the user.

### Native Measurement Flow

The sequence below illustrates how the native backend interacts with Cloudflare's endpoints, including the TCP/TLS warm-up phase and the subsequent measurements.

```mermaid
sequenceDiagram
    participant User as jc-speedtest CLI
    participant Native as NativeBackend
    participant CF as Cloudflare API
    
    User->>Native: measure()
    
    Note over Native,CF: Phase 1: Latency Warm-up
    Native->>CF: GET /__down?bytes=0 (Discarded)
    CF-->>Native: 200 OK (TCP/TLS Handshake paid)
    
    Note over Native,CF: Phase 2: True Latency (5 samples)
    loop 5 times
        Native->>CF: GET /__down?bytes=0
        CF-->>Native: 200 OK
    end
    Note over Native: Calculates median (ping_ms)
    
    Note over Native,CF: Phase 3: Download (25 MB)
    Native->>CF: GET /__down?bytes=25000000
    CF-->>Native: 200 OK (25MB Stream)
    Note over Native: Calculates Mbps = (bytes * 8) / time
    
    Note over Native,CF: Phase 4: Upload (10 MB)
    Native->>CF: POST /__up (10MB Payload)
    CF-->>Native: 200 OK
    Note over Native: Calculates Mbps = (bytes * 8) / time
    
    Native-->>User: SpeedtestResult (Immutable)
```

## Consequences
- **Pros**:
  - The package remains lightweight by default (only depends on `httpx`).
  - Fast startup time for automated scripts and CI/CD pipelines (no Python overhead of loading Ookla's multi-server libraries).
  - Predictable behavior: the user knows exactly which backend is being used unless they override it.
- **Cons**:
  - Users needing maximum accuracy on gigabit+ connections must manually opt-in by installing the extra and passing `--backend speedtest-cli`.
  - Upload measurement in native mode (single TCP stream) may be slightly less accurate than dedicated tools that use multiple parallel connections.
  - Clear documentation is required so users understand why `speedtest-cli` is not selected automatically.
