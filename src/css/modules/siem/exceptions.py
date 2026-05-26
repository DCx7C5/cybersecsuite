"""SIEM module exceptions."""


class SiemError(RuntimeError):
    """Base SIEM domain exception."""


class SiemIngestError(SiemError):
    """Raised when SIEM ingestion fails."""


class SiemResponseError(SiemError):
    """Raised when SIEM response action fails."""


__all__ = ["SiemError", "SiemIngestError", "SiemResponseError"]
