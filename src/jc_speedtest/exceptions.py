"""Custom exceptions for jc-speedtest."""


class JCSpeedtestError(Exception):
    """Base exception for all jc-speedtest errors."""


class MeasurementTimeoutError(JCSpeedtestError):
    """Raised when a measurement exceeds the configured timeout."""


class NoBackendAvailableError(JCSpeedtestError):
    """Raised when no measurement backend can be used."""


class MeasurementFailedError(JCSpeedtestError):
    """Raised when a measurement fails for an unexpected reason."""
