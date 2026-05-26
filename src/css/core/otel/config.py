"""OpenTelemetry config surface (lightweight placeholder)."""


import os

import msgspec


class OTelConfig(msgspec.Struct, frozen=True, kw_only=True):
    enabled: bool = False
    service_name: str = "cybersecsuite"
    exporter_endpoint: str | None = None


def get_otel_config() -> OTelConfig:
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    return OTelConfig(
        enabled=bool(os.environ.get("OTEL_ENABLED", "").lower() in {"1", "true", "yes"}),
        service_name=os.environ.get("OTEL_SERVICE_NAME", "cybersecsuite"),
        exporter_endpoint=endpoint if endpoint else None,
    )


__all__ = ["OTelConfig", "get_otel_config"]
