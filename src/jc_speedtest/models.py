"""Data models for jc-speedtest results."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

BackendName = Literal["native", "speedtest-cli"]


@dataclass(frozen=True, slots=True)
class SpeedtestResult:
    """Immutable result of a speed test run."""

    download_mbps: float | None
    upload_mbps: float | None
    ping_ms: float | None
    backend: BackendName
    server: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-friendly dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data
