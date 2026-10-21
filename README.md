# JC Speedtest

Lightweight, programmatic internet speed test for Python. No browser, no ads, no friction.

## Why?

Measuring internet speed through a browser is noisy: ads, JavaScript, and UI overhead.
`jc-speedtest` gives you clean measurements from the terminal or directly in your Python code.

## Installation

```bash
pip install jc-speedtest
```

For improved accuracy (optional):
```bash
pip install jc-speedtest[speedtest]
```

## Usage

### CLI
```bash
jc-speedtest
jc-speedtest --json
jc-speedtest --no-upload
```

### Python API
```python
from jc_speedtest import run_speedtest

result = run_speedtest()
print(f"Download: {result.download_mbps} Mbps")
print(f"Upload: {result.upload_mbps} Mbps")
print(f"Latency: {result.ping_ms} ms")
```

## License
MIT