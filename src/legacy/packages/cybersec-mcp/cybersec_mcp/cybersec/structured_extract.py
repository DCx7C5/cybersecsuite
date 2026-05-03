"""Structured extraction tools — use Anthropic messages.parse() for typed forensic output.

Implements Pydantic-based structured extraction for:
  - IOC extraction from raw text / logs
  - Finding classification
  - CVE context enrichment
  - Threat actor profiling
"""
from __future__ import annotations

import os
from typing import Any

from ..helpers import JsonDict, sdk_error, sdk_result
from ..sdk_compat import tool

# ── Pydantic schemas ─────────────────────────────────────────────────────────

try:
    from pydantic import BaseModel, Field

    class IOCItem(BaseModel):
        ioc_type: str = Field(description="ip, domain, url, hash_md5, hash_sha1, hash_sha256, email, filepath")
        value: str = Field(description="The indicator value")
        confidence: str = Field(description="low, medium, high, confirmed")
        context: str = Field(description="Brief context explaining why this is suspicious")

    class IOCExtraction(BaseModel):
        iocs: list[IOCItem] = Field(description="Extracted indicators of compromise")
        summary: str = Field(description="One-line summary of what was found")
        threat_type: str = Field(description="malware, phishing, c2, data_exfil, lateral_movement, other")

    class FindingClassification(BaseModel):
        severity: str = Field(description="low, medium, high, critical")
        category: str = Field(description="e.g. authentication, injection, exposure, privilege_escalation")
        cwe_ids: list[str] = Field(default_factory=list, description="Related CWE IDs, e.g. ['CWE-89']")
        mitre_techniques: list[str] = Field(default_factory=list, description="ATT&CK technique IDs, e.g. ['T1059.001']")
        remediation: str = Field(description="Concise remediation guidance")
        exploitability: str = Field(description="not_exploitable, theoretical, functional, weaponized")

    class ThreatActorProfile(BaseModel):
        name: str = Field(description="Actor name or alias")
        aliases: list[str] = Field(default_factory=list, description="Known aliases")
        motivation: str = Field(description="financial, espionage, hacktivism, destruction, unknown")
        sophistication: str = Field(description="low, medium, high, nation_state")
        targeted_sectors: list[str] = Field(default_factory=list)
        ttps: list[str] = Field(default_factory=list, description="ATT&CK technique IDs")
        infrastructure: list[str] = Field(default_factory=list, description="IPs, domains, ASNs used")

    class CVEContext(BaseModel):
        cve_id: str
        cvss_score: float = Field(ge=0.0, le=10.0)
        attack_vector: str = Field(description="network, adjacent, local, physical")
        attack_complexity: str = Field(description="low, high")
        privileges_required: str = Field(description="none, low, high")
        affected_products: list[str] = Field(default_factory=list)
        patch_available: bool
        exploitation_status: str = Field(description="unproven, poc, actively_exploited, weaponized")
        recommended_action: str

    class NetworkAnomalyAnalysis(BaseModel):
        anomaly_type: str = Field(description="port_scan, beaconing, exfil, lateral, dos, other")
        source_ips: list[str] = Field(default_factory=list)
        destination_ips: list[str] = Field(default_factory=list)
        protocols: list[str] = Field(default_factory=list)
        estimated_severity: str = Field(description="low, medium, high, critical")
        is_false_positive: bool
        recommended_block: bool

    _SCHEMAS: dict[str, type[BaseModel]] = {
        "ioc_extraction": IOCExtraction,
        "finding_classification": FindingClassification,
        "threat_actor_profile": ThreatActorProfile,
        "cve_context": CVEContext,
        "network_anomaly": NetworkAnomalyAnalysis,
    }
    _PYDANTIC_OK = True

except ImportError:
    _PYDANTIC_OK = False
    _SCHEMAS = {}


# ── Tool implementations ──────────────────────────────────────────────────────


@tool(
    "structured_extract",
    "Extract structured forensic data from text using a typed schema. Returns a validated JSON object.",
    {
        "text": {"type": "string", "description": "The raw text, log snippet, or report to extract from"},
        "schema": {
            "type": "string",
            "description": (
                "Schema to extract into. One of: "
                "ioc_extraction, finding_classification, threat_actor_profile, "
                "cve_context, network_anomaly"
            ),
        },
        "model": {"type": "string", "description": "Model to use", "default": "claude-haiku-4-5"},
        "system": {"type": "string", "description": "Optional system prompt override"},
    },
)
async def structured_extract(args: dict[str, Any]) -> JsonDict:
    if not _PYDANTIC_OK:
        return sdk_error("pydantic is not installed")

    text = str(args.get("text", "")).strip()
    schema_name = str(args.get("schema", "ioc_extraction")).strip().lower()
    model = str(args.get("model", os.environ.get("CYBERSEC_DEFAULT_MODEL", "claude-haiku-4-5")))
    system = args.get("system")

    if not text:
        return sdk_error("text is required")
    if schema_name not in _SCHEMAS:
        return sdk_error(
            f"Unknown schema '{schema_name}'. Available: {', '.join(_SCHEMAS)}"
        )

    schema_cls = _SCHEMAS[schema_name]

    try:
        import anthropic

        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
        client = anthropic.Anthropic(api_key=api_key, base_url=base_url)

        messages: list[dict] = [{"role": "user", "content": text}]
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": 2048,
            "output_format": schema_cls,
        }
        if system:
            kwargs["system"] = system

        result = client.messages.parse(**kwargs)
        parsed = result.parsed_output

        if parsed is None:
            return sdk_error("Model returned no structured output")

        return sdk_result({
            "schema": schema_name,
            "data": parsed.model_dump(),
            "model": model,
            "input_tokens": result.usage.input_tokens,
            "output_tokens": result.usage.output_tokens,
        })

    except Exception as exc:
        return sdk_error(f"structured_extract failed: {exc}")


@tool(
    "structured_extract_stream",
    "Stream structured extraction with incremental parsed snapshots (for large documents).",
    {
        "text": {"type": "string", "description": "The raw text to extract from"},
        "schema": {
            "type": "string",
            "description": "Schema: ioc_extraction, finding_classification, threat_actor_profile, cve_context, network_anomaly",
        },
        "model": {"type": "string", "default": "claude-haiku-4-5"},
    },
)
async def structured_extract_stream(args: dict[str, Any]) -> JsonDict:
    if not _PYDANTIC_OK:
        return sdk_error("pydantic is not installed")

    text = str(args.get("text", "")).strip()
    schema_name = str(args.get("schema", "ioc_extraction")).strip().lower()
    model = str(args.get("model", os.environ.get("CYBERSEC_DEFAULT_MODEL", "claude-haiku-4-5")))

    if not text:
        return sdk_error("text is required")
    if schema_name not in _SCHEMAS:
        return sdk_error(f"Unknown schema '{schema_name}'. Available: {', '.join(_SCHEMAS)}")

    schema_cls = _SCHEMAS[schema_name]

    try:
        import anthropic

        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
        client = anthropic.Anthropic(api_key=api_key, base_url=base_url)

        final_parsed = None
        final_usage = None

        with client.messages.stream(
            model=model,
            messages=[{"role": "user", "content": text}],
            max_tokens=2048,
            output_format=schema_cls,
        ) as stream:
            for _event in stream:
                pass  # consume stream — snapshots are available but not stored per-event
            final_msg = stream.get_final_message()
            final_parsed = final_msg.parsed_output
            final_usage = final_msg.usage

        if final_parsed is None:
            return sdk_error("Model returned no structured output")

        return sdk_result({
            "schema": schema_name,
            "data": final_parsed.model_dump(),
            "model": model,
            "input_tokens": final_usage.input_tokens if final_usage else 0,
            "output_tokens": final_usage.output_tokens if final_usage else 0,
        })

    except Exception as exc:
        return sdk_error(f"structured_extract_stream failed: {exc}")


ALL_TOOLS = [structured_extract, structured_extract_stream]
