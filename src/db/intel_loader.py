from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree

from tortoise.context import get_current_context

from db.models.cve import CVEIntel
from db.models.cve_entry import CVEIntelligenceEntry
from db.models.cwe import CWEIntel
from db.models.capec import CapecAttackPatternIntel
from db.models.feed_snapshot import ThreatIntelFeedSnapshot
from db.models.ioc_entry import IOCDatabaseEntry
from db.models.misp import MISPAttributeIntel, MISPEventIntel
from db.models.mitre_actor import MitreThreatActorIntel
from db.models.opencti import OpenCTIEntityIntel, OpenCTIIndicatorIntel
from db.models.mitre_software import MitreSoftwareFamilyIntel
from db.models.mitre_technique import MitreTechniqueIntel
from db.models.references import (
    ThreatActorTechniqueReference,
    CWECAPECReference,
    CAPECMitreTechniqueReference,
    ThreatActorSoftwareReference,
    SoftwareTechniqueReference,
)
from db.models.threat_intel import ForensicMITRETechnique
from db.models.threat_profile_entry import ThreatProfileEntry
from db.models.update_log_entry import IntelligenceUpdateLogEntry
from db.models.enums import MITRETactic

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_INTEL_DIR = _PROJECT_ROOT / "data" / "cybersec-shared" / "intelligence"
_JSON_DECODER = json.JSONDecoder()
_UPDATE_LOG_PATTERN = re.compile(r"^\[(?P<run_id>[^]]+)]\s+(?P<category>[^:]+):\s+(?P<status>[^-]+)-\s+(?P<message>.+)$")
_ATTACK_GROUP_RE = re.compile(r"https?://attack\.mitre\.org/groups/(?P<group_id>G\d{4,})")
_ATTACK_TECHNIQUE_RE = re.compile(r"https?://attack\.mitre\.org/techniques/(?P<path>T\d{4}(?:/\d{3})?)/?")
_CAPEC_EXTERNAL_ID_RE = re.compile(r"CAPEC-\d+")
_STIX_PATTERN_VALUE_RE = re.compile(r"=\s*(?:'([^']+)'|\"([^\"]+)\")")


@dataclass(slots=True)
class BootstrapStats:
    name: str
    source_file: str | None = None
    status: str = "pending"
    processed: int = 0
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[str] | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "source_file": self.source_file,
            "status": self.status,
            "processed": self.processed,
            "inserted": self.inserted,
            "updated": self.updated,
            "skipped": self.skipped,
            "errors": self.errors or [],
        }


def get_intelligence_root() -> Path:
    raw = os.environ.get("CYBERSEC_INTEL_DIR")
    return Path(raw).expanduser().resolve() if raw else _DEFAULT_INTEL_DIR


def _relative_source(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(_PROJECT_ROOT))
    except ValueError:
        return str(path.resolve())


def _snapshot_id(path: Path) -> str:
    stat = path.stat()
    payload = f"{path.resolve()}:{stat.st_size}:{stat.st_mtime_ns}".encode("utf-8")
    return hashlib.sha1(payload).hexdigest()[:20]


async def _snapshot_is_current(path: Path, force: bool = False) -> tuple[str, ThreatIntelFeedSnapshot | None, bool]:
    snapshot_id = _snapshot_id(path)
    if force:
        return snapshot_id, None, False

    source_file = _relative_source(path)
    existing = await ThreatIntelFeedSnapshot.get_or_none(source_file=source_file)
    return snapshot_id, existing, bool(existing and existing.snapshot_id == snapshot_id)


def _count_payload_records(payload: Any) -> int:
    if isinstance(payload, list):
        return len(payload)
    if isinstance(payload, dict):
        for field_name in ("objects", "response", "data", "records", "items", "values"):
            value = payload.get(field_name)
            if isinstance(value, list):
                return len(value)
        records_value = payload.get("records")
        if isinstance(records_value, int):
            return records_value
    return 0


def _classify_feed_snapshot(path: Path, payload: Any) -> dict[str, Any]:
    stem = path.stem.lower()
    provider = "generic"
    feed_kind = "snapshot"
    source_url = ""

    if stem.startswith("misp-"):
        provider = "misp"
        feed_kind = "event_export"
    elif stem.startswith("opencti-"):
        provider = "opencti"
        feed_kind = "export"
    elif stem.startswith("circl-"):
        provider = "circl"
        feed_kind = "hashlookup"
        source_url = "https://hashlookup.circl.lu/info"
    elif stem.startswith("abusech-"):
        provider = "abusech"
        feed_kind = "threat_feed"
        source_url = "https://bazaar.abuse.ch/export/json/recent/"
    elif stem.startswith("capec-"):
        provider = "mitre"
        feed_kind = "capec"

    return {
        "provider": provider,
        "feed_kind": feed_kind,
        "source_url": source_url,
        "record_count": _count_payload_records(payload),
    }


async def _store_snapshot(path: Path, snapshot_id: str, feed_name: str, payload: dict[str, Any], **extra: Any) -> None:
    source_file = _relative_source(path)
    existing = await ThreatIntelFeedSnapshot.get_or_none(source_file=source_file)
    defaults = {
        "provider": extra.get("provider", "internal"),
        "feed_name": feed_name,
        "feed_kind": extra.get("feed_kind", feed_name),
        "snapshot_id": snapshot_id,
        "source_url": extra.get("source_url", ""),
        "record_count": extra.get("record_count", _count_payload_records(payload)),
        "payload": payload,
    }
    if existing:
        existing.provider = defaults["provider"]
        existing.feed_name = feed_name
        existing.feed_kind = defaults["feed_kind"]
        existing.snapshot_id = snapshot_id
        existing.source_url = defaults["source_url"]
        existing.record_count = defaults["record_count"]
        existing.payload = payload
        await existing.save()
    else:
        await ThreatIntelFeedSnapshot.create(
            provider=defaults["provider"],
            feed_name=feed_name,
            feed_kind=defaults["feed_kind"],
            snapshot_id=snapshot_id,
            source_file=source_file,
            source_url=defaults["source_url"],
            record_count=defaults["record_count"],
            payload=payload,
        )


def _read_json_document(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))


def _load_stix_objects(path: Path) -> list[dict[str, Any]]:
    document = _read_json_document(path)
    objects = document.get("objects", []) if isinstance(document, dict) else []
    return [obj for obj in objects if isinstance(obj, dict)]


def _extract_external_id(record: dict[str, Any], source_names: set[str]) -> str:
    for reference in record.get("external_references") or []:
        source_name = str(reference.get("source_name") or "").lower()
        if source_name in source_names:
            external_id = str(reference.get("external_id") or "").strip()
            if external_id:
                return external_id
    return ""


def _extract_external_url(record: dict[str, Any], source_names: set[str]) -> str:
    for reference in record.get("external_references") or []:
        source_name = str(reference.get("source_name") or "").lower()
        if source_name in source_names:
            url = str(reference.get("url") or "").strip()
            if url:
                return url
    return ""


def _extract_capec_ids_from_attack_pattern(record: dict[str, Any]) -> list[str]:
    capec_ids: list[str] = []
    for reference in record.get("external_references") or []:
        source_name = str(reference.get("source_name") or "").lower()
        external_id = str(reference.get("external_id") or "").strip().upper()
        if source_name == "capec" and _CAPEC_EXTERNAL_ID_RE.fullmatch(external_id):
            capec_ids.append(external_id)
    return list(dict.fromkeys(capec_ids))


def _latest_matching_file(directory: Path, pattern: str) -> Path | None:
    files = [path for path in directory.glob(pattern) if path.is_file()]
    if not files:
        return None
    return max(files, key=lambda path: (path.stat().st_mtime_ns, path.name))


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        timestamp = float(value)
        if timestamp > 1_000_000_000_000:
            timestamp /= 1000
        try:
            # Keep stored values naive-UTC while avoiding deprecated utcfromtimestamp.
            return datetime.fromtimestamp(timestamp, UTC).replace(tzinfo=None)
        except (OverflowError, OSError, ValueError):
            return None
    raw = str(value).strip()
    if not raw:
        return None
    if raw.isdigit():
        timestamp = float(raw)
        if timestamp > 1_000_000_000_000:
            timestamp /= 1000
        try:
            return datetime.fromtimestamp(timestamp, UTC).replace(tzinfo=None)
        except (OverflowError, OSError, ValueError):
            return None
    normalized = raw.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
        return parsed.replace(tzinfo=None) if parsed.tzinfo else parsed
    except ValueError:
        return None


def _snapshot_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, list):
        return {"items": payload}
    return {"value": payload}


def _dedupe_strings(values: Iterable[Any]) -> list[str]:
    items: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in items:
            items.append(text)
    return items


def _normalize_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "yes", "on", "published"}


def _safe_int(value: Any) -> int | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None


def _safe_float(value: Any) -> float | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def _extract_tag_names(value: Any) -> list[str]:
    if isinstance(value, dict):
        for field_name in ("Tag", "tags", "items", "nodes"):
            nested = value.get(field_name)
            if nested is not None:
                return _extract_tag_names(nested)
        name = value.get("name") or value.get("value") or value.get("label")
        return _dedupe_strings([name])
    if isinstance(value, list):
        tags: list[str] = []
        for item in value:
            tags.extend(_extract_tag_names(item))
        return _dedupe_strings(tags)
    return _dedupe_strings([value])


def _normalize_ioc_type(value_type: Any, category: Any = None, value: Any = None) -> str:
    normalized = str(value_type or "").strip().lower().replace("-", "_").replace(" ", "_")
    mapping = {
        "ip": "ip_address",
        "ip_src": "ip_address",
        "ip_dst": "ip_address",
        "ipv4_addr": "ip_address",
        "ipv6_addr": "ip_address",
        "domain": "domain",
        "hostname": "domain",
        "domain_name": "domain",
        "url": "url",
        "uri": "url",
        "email": "email_address",
        "email_src": "email_address",
        "email_dst": "email_address",
        "email_addr": "email_address",
        "email_subject": "email_subject",
        "file_hash": "file_hash",
        "md5": "file_hash",
        "sha1": "file_hash",
        "sha224": "file_hash",
        "sha256": "file_hash",
        "sha384": "file_hash",
        "sha512": "file_hash",
        "filename": "file_path",
        "filepath": "file_path",
        "file_path": "file_path",
        "directory": "file_path",
        "process": "process_name",
        "process_name": "process_name",
        "mutex": "mutex",
        "regkey": "registry_key",
        "registry_key": "registry_key",
        "user_agent": "user_agent",
    }
    if normalized in mapping:
        return mapping[normalized]
    if "hash" in normalized:
        return "file_hash"
    raw_value = str(value or "")
    if "@" in raw_value and normalized in {"", "text", "string"}:
        return "email_address"
    category_normalized = str(category or "").strip().lower().replace("-", "_").replace(" ", "_")
    if category_normalized in mapping:
        return mapping[category_normalized]
    return normalized or category_normalized or "indicator"


def _confidence_from_numeric(value: Any) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return ""
    if numeric >= 90:
        return "confirmed"
    if numeric >= 70:
        return "high"
    if numeric >= 40:
        return "medium"
    return "low"


def _pick_confidence(*values: Any) -> str:
    rank = {"": 0, "low": 1, "medium": 2, "high": 3, "confirmed": 4}
    selected = ""
    for value in values:
        normalized = str(value or "").strip().lower()
        if normalized not in rank:
            normalized = _confidence_from_numeric(value)
        if rank.get(normalized, 0) > rank.get(selected, 0):
            selected = normalized
    return selected


def _extract_misp_events(payload: Any) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []

    def collect(node: Any) -> None:
        if isinstance(node, list):
            for item in node:
                collect(item)
            return
        if not isinstance(node, dict):
            return
        if isinstance(node.get("Event"), dict):
            events.append(node["Event"])
            return
        if node.get("Attribute") is not None and any(field_name in node for field_name in ("uuid", "id", "info")):
            events.append(node)
            return
        for field_name in ("response", "events", "data", "result"):
            if field_name in node:
                collect(node[field_name])

    collect(payload)
    return events


def _extract_misp_attributes(event: dict[str, Any]) -> list[dict[str, Any]]:
    raw_attributes = event.get("Attribute") or event.get("attributes") or []
    if isinstance(raw_attributes, dict):
        raw_attributes = [raw_attributes]
    attributes: list[dict[str, Any]] = []
    for item in raw_attributes:
        if isinstance(item, dict) and isinstance(item.get("Attribute"), dict):
            attributes.append(item["Attribute"])
        elif isinstance(item, dict):
            attributes.append(item)
    return attributes


def _misp_attribute_uuid(event_uuid: str, attribute: dict[str, Any]) -> str:
    value = str(attribute.get("uuid") or "").strip()
    if value:
        return value
    attribute_id = str(attribute.get("id") or "").strip()
    if attribute_id:
        return f"{event_uuid}:{attribute_id}"
    payload = json.dumps(
        {
            "event_uuid": event_uuid,
            "category": attribute.get("category"),
            "type": attribute.get("type"),
            "value": attribute.get("value"),
        },
        sort_keys=True,
    )
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:40]


def _extract_opencti_objects(payload: Any) -> list[dict[str, Any]]:
    objects: list[dict[str, Any]] = []
    visited: set[int] = set()

    def collect(node: Any) -> None:
        if id(node) in visited:
            return
        visited.add(id(node))
        if isinstance(node, list):
            for item in node:
                collect(item)
            return
        if not isinstance(node, dict):
            return
        object_type = str(node.get("type") or node.get("entity_type") or node.get("x_opencti_type") or "").strip()
        object_id = str(node.get("standard_id") or node.get("id") or "").strip()
        if object_type and (object_id or node.get("name") or node.get("pattern")):
            objects.append(node)
        for field_name in ("objects", "data", "entities", "nodes", "edges", "result", "items"):
            nested = node.get(field_name)
            if field_name == "edges" and isinstance(nested, list):
                for edge in nested:
                    if isinstance(edge, dict) and "node" in edge:
                        collect(edge.get("node"))
                    else:
                        collect(edge)
            else:
                collect(nested)

    collect(payload)
    deduped: dict[str, dict[str, Any]] = {}
    for obj in objects:
        object_key = str(obj.get("standard_id") or obj.get("id") or f"{obj.get('type')}:{obj.get('name')}:{len(deduped)}")
        deduped[object_key] = obj
    return list(deduped.values())


def _extract_opencti_labels(record: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for field_name in ("labels", "x_opencti_labels"):
        if field_name in record:
            values.extend(_extract_tag_names(record.get(field_name)))
    object_label = record.get("objectLabel")
    if isinstance(object_label, dict):
        values.extend(_extract_tag_names(object_label.get("edges") or object_label.get("nodes") or object_label))
    return _dedupe_strings(values)


def _extract_opencti_external_references(record: dict[str, Any]) -> list[dict[str, Any]]:
    references = record.get("external_references") or record.get("externalReferences") or []
    if isinstance(references, dict):
        references = references.get("edges") or references.get("nodes") or []
    normalized: list[dict[str, Any]] = []
    for item in references:
        if isinstance(item, dict) and isinstance(item.get("node"), dict):
            item = item["node"]
        if isinstance(item, dict):
            normalized.append(item)
    return normalized


def _extract_opencti_observable_values(pattern: Any) -> list[str]:
    if not pattern:
        return []
    values: list[str] = []
    for match in _STIX_PATTERN_VALUE_RE.finditer(str(pattern)):
        value = match.group(1) or match.group(2)
        if value and value not in values:
            values.append(value)
    return values


def _extract_opencti_created_by(record: dict[str, Any]) -> str:
    created_by = record.get("createdBy") or record.get("created_by") or record.get("created_by_ref")
    if isinstance(created_by, dict):
        return str(created_by.get("name") or created_by.get("id") or "").strip()
    return str(created_by or "").strip()


def _extract_attack_ids_from_external_references(references: Iterable[dict[str, Any]]) -> list[str]:
    technique_ids: list[str] = []
    for reference in references:
        external_id = str(reference.get("external_id") or "").strip()
        if re.fullmatch(r"T\d{4}(?:\.\d{3})?", external_id) and external_id not in technique_ids:
            technique_ids.append(external_id)
    return technique_ids


def _severity_from_score(score: float | None) -> str:
    if score is None:
        return ""
    if score >= 9.0:
        return "critical"
    if score >= 7.0:
        return "high"
    if score >= 4.0:
        return "medium"
    return "low"


def _iter_json_objects(path: Path) -> Iterable[dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    index = 0
    length = len(text)
    while index < length:
        while index < length and text[index].isspace():
            index += 1
        if index >= length:
            break
        if text[index] == ',':
            index += 1
            continue
        obj, index = _JSON_DECODER.raw_decode(text, index)
        if isinstance(obj, dict):
            yield obj
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, dict):
                    yield item


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _child_text(element: ElementTree.Element, child_name: str) -> str | None:
    for child in element:
        if _local_name(child.tag) == child_name and child.text:
            return child.text.strip()
    return None


def _descendant_texts(element: ElementTree.Element, local_name: str) -> list[str]:
    values: list[str] = []
    for child in element.iter():
        if _local_name(child.tag) == local_name and child.text:
            value = child.text.strip()
            if value and value not in values:
                values.append(value)
    return values


def _extract_cwe_records(path: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for _event, elem in ElementTree.iterparse(path, events=("end",)):
        if _local_name(elem.tag) != "Weakness":
            continue

        cwe_id = elem.attrib.get("ID")
        name = elem.attrib.get("Name")
        if not cwe_id or not name:
            elem.clear()
            continue

        common_consequences: list[dict[str, Any]] = []
        for consequence in elem.iter():
            if _local_name(consequence.tag) != "Consequence":
                continue
            scopes = _descendant_texts(consequence, "Scope")
            impacts = _descendant_texts(consequence, "Impact")
            note = next((text for text in _descendant_texts(consequence, "Note")), "")
            common_consequences.append({
                "scopes": scopes,
                "impacts": impacts,
                "note": note,
            })

        related_attack_patterns: list[str] = []
        for related in elem.iter():
            if _local_name(related.tag) != "Related_Attack_Pattern":
                continue
            capec_id = related.attrib.get("CAPEC_ID") or related.attrib.get("ID")
            if capec_id and capec_id not in related_attack_patterns:
                related_attack_patterns.append(capec_id)

        description = _child_text(elem, "Description")
        extended_description = _child_text(elem, "Extended_Description")
        record = {
            "name": name,
            "abstraction": elem.attrib.get("Abstraction"),
            "status": elem.attrib.get("Status"),
            "description": description,
            "extended_description": extended_description,
            "likelihood_of_exploit": _child_text(elem, "Likelihood_Of_Exploit"),
            "common_consequences": common_consequences,
            "detection_methods": _descendant_texts(elem, "Method"),
            "mitigations": _descendant_texts(elem, "Strategy") + _descendant_texts(elem, "Description"),
            "related_attack_patterns": related_attack_patterns,
            "raw_record": {
                "cwe_id": f"CWE-{cwe_id}",
                "name": name,
                "abstraction": elem.attrib.get("Abstraction"),
                "status": elem.attrib.get("Status"),
            },
        }
        # De-duplicate mitigation texts while preserving order.
        mitigation_values = [text for text in record["mitigations"] if isinstance(text, str)]
        record["mitigations"] = list(dict.fromkeys(text for text in mitigation_values if text))
        records[f"CWE-{cwe_id}"] = record
        elem.clear()
    return records


def _map_tactic_name(values: list[str]) -> MITRETactic:
    for value in values:
        normalized = value.strip().replace("-", "_").replace(" ", "_").upper()
        if normalized in MITRETactic.__members__:
            return MITRETactic[normalized]
    return MITRETactic.DISCOVERY


def _technique_url(technique_id: str) -> str:
    if not technique_id:
        return ""
    if "." in technique_id:
        parent, child = technique_id.split(".", 1)
        return f"https://attack.mitre.org/techniques/{parent}/{child}/"
    return f"https://attack.mitre.org/techniques/{technique_id}/"


def _extract_group_url(description: str | None) -> str:
    if not description:
        return ""
    match = _ATTACK_GROUP_RE.search(description)
    if not match:
        return ""
    return match.group(0)


def _extract_technique_ids(text: str | None) -> list[str]:
    if not text:
        return []
    return list(dict.fromkeys(match.group(1) for match in re.finditer(r"\b(T\d{4}(?:\.\d{3})?)\b", text)))


def _apply_updates(obj: Any, defaults: dict[str, Any]) -> bool:
    changed = False
    for field_name, new_value in defaults.items():
        if getattr(obj, field_name) != new_value:
            setattr(obj, field_name, new_value)
            changed = True
    return changed


async def _sync_cve_entries(source_file: str, records: list[dict[str, Any]]) -> None:
    await CVEIntelligenceEntry.filter(source_file=source_file).delete()
    entries = [
        CVEIntelligenceEntry(
            cve_identifier=record["cve_id"],
            cve_id=record.get("cve_pk"),
            score=record.get("score"),
            description=record.get("description"),
            published_at=record.get("published_at"),
            line_number=index,
            source_file=source_file,
            raw_record=record.get("raw_record", {}),
        )
        for index, record in enumerate(records, start=1)
    ]
    if entries:
        await CVEIntelligenceEntry.bulk_create(entries, batch_size=500)


async def _upsert_ioc_database_entries(records: list[dict[str, Any]]) -> dict[str, int]:
    if not records:
        return {"processed": 0, "inserted": 0, "updated": 0, "skipped": 0}

    merged: dict[tuple[str, str], dict[str, Any]] = {}
    for record in records:
        ioc_type = str(record.get("ioc_type") or "").strip()
        value = str(record.get("value") or "").strip()
        if not ioc_type or not value:
            continue
        key = (ioc_type, value)
        current = merged.get(key)
        if current is None:
            merged[key] = {
                "ioc_type": ioc_type,
                "value": value,
                "confidence": _pick_confidence(record.get("confidence")),
                "tags": _dedupe_strings(record.get("tags") or []),
                "context": str(record.get("context") or "").strip() or None,
                "first_seen": _parse_datetime(record.get("first_seen")),
                "last_seen": _parse_datetime(record.get("last_seen")),
                "source_file": str(record.get("source_file") or ""),
                "raw_record": record.get("raw_record") or {},
            }
            continue

        current["confidence"] = _pick_confidence(current.get("confidence"), record.get("confidence"))
        current["tags"] = _dedupe_strings((current.get("tags") or []) + (record.get("tags") or []))
        if not current.get("context") and record.get("context"):
            current["context"] = str(record.get("context")).strip()
        record_first_seen = _parse_datetime(record.get("first_seen"))
        record_last_seen = _parse_datetime(record.get("last_seen"))
        if record_first_seen and (current.get("first_seen") is None or record_first_seen < current["first_seen"]):
            current["first_seen"] = record_first_seen
        if record_last_seen and (current.get("last_seen") is None or record_last_seen > current["last_seen"]):
            current["last_seen"] = record_last_seen
        if record.get("source_file"):
            current["source_file"] = str(record["source_file"])
        current["raw_record"] = record.get("raw_record") or current.get("raw_record") or {}

    values = [defaults["value"] for defaults in merged.values()]
    existing_rows = await IOCDatabaseEntry.filter(value__in=values).all()
    existing = {(row.ioc_type, row.value): row for row in existing_rows}

    stats = {"processed": len(merged), "inserted": 0, "updated": 0, "skipped": 0}
    to_create: list[IOCDatabaseEntry] = []
    for key, defaults in merged.items():
        current = existing.get(key)
        if current:
            updated_defaults = {
                **defaults,
                "tags": _dedupe_strings((current.tags or []) + (defaults.get("tags") or [])),
                "confidence": _pick_confidence(current.confidence, defaults.get("confidence")),
                "context": current.context or defaults.get("context"),
                "first_seen": min(filter(None, [current.first_seen, defaults.get("first_seen")]), default=None),
                "last_seen": max(filter(None, [current.last_seen, defaults.get("last_seen")]), default=None),
            }
            if _apply_updates(current, updated_defaults):
                await current.save()
                stats["updated"] += 1
            else:
                stats["skipped"] += 1
        else:
            to_create.append(IOCDatabaseEntry(**defaults))
    if to_create:
        await IOCDatabaseEntry.bulk_create(to_create, batch_size=500)
        stats["inserted"] = len(to_create)
    return stats


async def _upsert_threat_profile_entries(records: list[dict[str, Any]]) -> dict[str, int]:
    if not records:
        return {"processed": 0, "inserted": 0, "updated": 0, "skipped": 0}

    merged: dict[str, dict[str, Any]] = {}
    for record in records:
        profile_name = str(record.get("profile_name") or "").strip()
        if not profile_name:
            continue
        current = merged.get(profile_name)
        if current is None:
            merged[profile_name] = {
                "profile_name": profile_name,
                "summary": record.get("summary"),
                "motivations": _dedupe_strings(record.get("motivations") or []),
                "sectors": _dedupe_strings(record.get("sectors") or []),
                "regions": _dedupe_strings(record.get("regions") or []),
                "ttps": _dedupe_strings(record.get("ttps") or []),
                "confidence_score": record.get("confidence_score"),
                "source_file": str(record.get("source_file") or ""),
                "raw_record": record.get("raw_record") or {},
            }
            if record.get("actor") is not None:
                merged[profile_name]["actor"] = record.get("actor")
            continue

        current["motivations"] = _dedupe_strings((current.get("motivations") or []) + (record.get("motivations") or []))
        current["sectors"] = _dedupe_strings((current.get("sectors") or []) + (record.get("sectors") or []))
        current["regions"] = _dedupe_strings((current.get("regions") or []) + (record.get("regions") or []))
        current["ttps"] = _dedupe_strings((current.get("ttps") or []) + (record.get("ttps") or []))
        if not current.get("summary") and record.get("summary"):
            current["summary"] = record.get("summary")
        if current.get("confidence_score") is None and record.get("confidence_score") is not None:
            current["confidence_score"] = record.get("confidence_score")
        if record.get("actor") is not None:
            current["actor"] = record.get("actor")
        if record.get("source_file"):
            current["source_file"] = str(record["source_file"])
        current["raw_record"] = record.get("raw_record") or current.get("raw_record") or {}

    existing_rows = await ThreatProfileEntry.filter(profile_name__in=list(merged.keys())).all()
    existing = {row.profile_name: row for row in existing_rows}
    stats = {"processed": len(merged), "inserted": 0, "updated": 0, "skipped": 0}
    to_create: list[ThreatProfileEntry] = []
    for profile_name, defaults in merged.items():
        current = existing.get(profile_name)
        if current:
            if _apply_updates(current, defaults):
                await current.save()
                stats["updated"] += 1
            else:
                stats["skipped"] += 1
        else:
            to_create.append(ThreatProfileEntry(**defaults))
    if to_create:
        await ThreatProfileEntry.bulk_create(to_create, batch_size=300)
        stats["inserted"] = len(to_create)
    return stats


async def bootstrap_cve_intelligence_async(force: bool = False) -> dict[str, Any]:
    intel_root = get_intelligence_root()
    source_path = intel_root / "cve-intelligence.md"
    stats = BootstrapStats(name="cve", source_file=_relative_source(source_path))
    if not source_path.exists():
        stats.status = "missing"
        stats.errors = [f"Source file not found: {source_path}"]
        return stats.as_dict()

    snapshot_id, _existing_snapshot, is_current = await _snapshot_is_current(source_path, force=force)
    if is_current:
        stats.status = "skipped"
        stats.skipped = 1
        return stats.as_dict()

    normalized_records: dict[str, dict[str, Any]] = {}
    line_entries: list[dict[str, Any]] = []
    for record in _iter_json_objects(source_path):
        cve_id = str(record.get("id") or record.get("cve_id") or "").strip()
        if not cve_id:
            continue
        score = float(record["score"]) if record.get("score") is not None else None
        published_at = _parse_datetime(record.get("published") or record.get("published_at"))
        normalized = {
            "cve_id": cve_id,
            "cvss_score": score,
            "cvss_vector": str(record.get("cvss_vector") or ""),
            "severity": _severity_from_score(score),
            "description": record.get("description"),
            "affected_products": record.get("affected_products") or [],
            "references": record.get("references") or [],
            "exploit_available": bool(record.get("exploit_available") or (score is not None and score >= 8.0)),
            "patch_available": bool(record.get("patch_available", False)),
            "published_at": published_at,
            "last_modified_at": _parse_datetime(record.get("last_modified") or record.get("last_modified_at")),
            "source_file": _relative_source(source_path),
            "source_feed": str(record.get("source_feed") or "shared-cve-intelligence"),
            "raw_record": record,
            "tags": record.get("tags") or [],
        }
        normalized_records[cve_id] = normalized
        line_entries.append({
            "cve_id": cve_id,
            "score": score,
            "description": record.get("description"),
            "published_at": published_at,
            "raw_record": record,
        })

    stats.processed = len(line_entries)
    existing = {
        obj.cve_id: obj
        for obj in await CVEIntel.filter(cve_id__in=list(normalized_records.keys())).all()
    }
    to_create: list[CVEIntel] = []
    entry_pk_map: dict[str, int] = {}
    for cve_id, defaults in normalized_records.items():
        current = existing.get(cve_id)
        if current:
            if _apply_updates(current, defaults):
                await current.save()
                stats.updated += 1
            else:
                stats.skipped += 1
            entry_pk_map[cve_id] = current.id
        else:
            to_create.append(CVEIntel(cve_id=cve_id, **defaults))
    if to_create:
        await CVEIntel.bulk_create(to_create, batch_size=500)
        stats.inserted += len(to_create)
        refreshed = await CVEIntel.filter(cve_id__in=[obj.cve_id for obj in to_create]).all()
        entry_pk_map.update({obj.cve_id: obj.id for obj in refreshed})

    for record in line_entries:
        record["cve_pk"] = entry_pk_map.get(record["cve_id"])
    await _sync_cve_entries(_relative_source(source_path), line_entries)

    await _store_snapshot(
        source_path,
        snapshot_id,
        "cve",
        {
            "records": stats.processed,
            "inserted": stats.inserted,
            "updated": stats.updated,
            "skipped": stats.skipped,
        },
    )
    stats.status = "ok"
    return stats.as_dict()


async def bootstrap_cwe_intelligence_async(force: bool = False) -> dict[str, Any]:
    intel_root = get_intelligence_root()
    cwe_dir = intel_root / "cwe"
    source_path = cwe_dir / "cwec_v4.19.1.xml"
    if not source_path.exists():
        source_path = _latest_matching_file(cwe_dir, "*.xml") or source_path

    stats = BootstrapStats(name="cwe", source_file=_relative_source(source_path))
    if not source_path.exists():
        stats.status = "missing"
        stats.errors = [f"Source file not found: {source_path}"]
        return stats.as_dict()

    snapshot_id, _existing_snapshot, is_current = await _snapshot_is_current(source_path, force=force)
    if is_current:
        stats.status = "skipped"
        stats.skipped = 1
        return stats.as_dict()

    records = _extract_cwe_records(source_path)
    stats.processed = len(records)
    existing = {
        obj.cwe_id: obj
        for obj in await CWEIntel.filter(cwe_id__in=list(records.keys())).all()
    }
    to_create: list[CWEIntel] = []
    for cwe_id, defaults in records.items():
        current = existing.get(cwe_id)
        defaults = {**defaults, "source_file": _relative_source(source_path)}
        if current:
            if _apply_updates(current, defaults):
                await current.save()
                stats.updated += 1
            else:
                stats.skipped += 1
        else:
            to_create.append(CWEIntel(cwe_id=cwe_id, **defaults))
    if to_create:
        await CWEIntel.bulk_create(to_create, batch_size=300)
        stats.inserted += len(to_create)

    await _store_snapshot(
        source_path,
        snapshot_id,
        "cwe",
        {
            "records": stats.processed,
            "inserted": stats.inserted,
            "updated": stats.updated,
            "skipped": stats.skipped,
        },
    )
    stats.status = "ok"
    return stats.as_dict()


async def bootstrap_capec_intelligence_async(force: bool = False) -> dict[str, Any]:
    intel_root = get_intelligence_root()
    capec_path = intel_root / "mitre" / "cti" / "capec" / "2.1" / "stix-capec.json"
    enterprise_path = intel_root / "mitre" / "cti" / "enterprise-attack" / "enterprise-attack.json"
    summary = {
        "patterns": BootstrapStats(name="capec_patterns", source_file=_relative_source(capec_path)).as_dict(),
        "cwe_refs": BootstrapStats(name="cwe_capec_refs", source_file=_relative_source(capec_path)).as_dict(),
        "mitre_refs": BootstrapStats(name="capec_mitre_refs", source_file=_relative_source(enterprise_path)).as_dict(),
    }

    if not capec_path.exists():
        for component in summary.values():
            component["status"] = "missing"
            component["errors"] = [f"Source file not found: {capec_path}"]
        return summary

    capec_stats = BootstrapStats(name="capec_patterns", source_file=_relative_source(capec_path))
    snapshot_id, _existing_snapshot, is_current = await _snapshot_is_current(capec_path, force=force)
    capec_records: dict[str, dict[str, Any]] = {}
    if is_current:
        capec_stats.status = "skipped"
        capec_stats.skipped = 1
    else:
        objects = _load_stix_objects(capec_path)
        capec_by_stix_id: dict[str, str] = {}
        parent_map: dict[str, set[str]] = {}
        child_map: dict[str, set[str]] = {}
        for obj in objects:
            if obj.get("type") != "attack-pattern":
                continue
            capec_id = _extract_external_id(obj, {"capec"})
            if not capec_id:
                continue
            capec_by_stix_id[str(obj.get("id") or "")] = capec_id
            capec_records[capec_id] = {
                "name": str(obj.get("name") or "").strip(),
                "description": obj.get("description"),
                "abstraction": str(obj.get("x_capec_abstraction") or ""),
                "domains": obj.get("x_capec_domains") or [],
                "prerequisites": obj.get("x_capec_prerequisites") or [],
                "resources_required": obj.get("x_capec_resources_required") or [],
                "skills_required": obj.get("x_capec_skills_required") or [],
                "consequences": obj.get("x_capec_consequences") or [],
                "execution_flow": obj.get("x_capec_execution_flow") or [],
                "example_instances": obj.get("x_capec_example_instances") or [],
                "parent_capec_ids": [],
                "child_capec_ids": [],
                "likelihood_of_attack": str(obj.get("x_capec_likelihood_of_attack") or ""),
                "severity": str(obj.get("x_capec_typical_severity") or ""),
                "url": _extract_external_url(obj, {"capec"}),
                "source_file": _relative_source(capec_path),
                "raw_record": obj,
                "tags": list(dict.fromkeys((obj.get("x_capec_domains") or []) + ["capec"])),
            }

        for obj in objects:
            if obj.get("type") != "relationship":
                continue
            source_id = capec_by_stix_id.get(str(obj.get("source_ref") or ""))
            target_id = capec_by_stix_id.get(str(obj.get("target_ref") or ""))
            if not source_id or not target_id:
                continue
            relationship_type = str(obj.get("relationship_type") or "")
            if relationship_type in {"subtechnique-of", "child-of"}:
                parent_map[source_id] = parent_map.get(source_id, set()) | {target_id}
                child_map[target_id] = child_map.get(target_id, set()) | {source_id}

        for capec_id, record in capec_records.items():
            record["parent_capec_ids"] = sorted(parent_map.get(capec_id, set()))
            record["child_capec_ids"] = sorted(child_map.get(capec_id, set()))

        capec_stats.processed = len(capec_records)
        existing = {
            obj.capec_id: obj
            for obj in await CapecAttackPatternIntel.filter(capec_id__in=list(capec_records.keys())).all()
        }
        to_create: list[CapecAttackPatternIntel] = []
        for capec_id, defaults in capec_records.items():
            current = existing.get(capec_id)
            if current:
                if _apply_updates(current, defaults):
                    await current.save()
                    capec_stats.updated += 1
                else:
                    capec_stats.skipped += 1
            else:
                to_create.append(CapecAttackPatternIntel(capec_id=capec_id, **defaults))
        if to_create:
            await CapecAttackPatternIntel.bulk_create(to_create, batch_size=300)
            capec_stats.inserted += len(to_create)

        await _store_snapshot(
            capec_path,
            snapshot_id,
            "capec-patterns",
            {
                "records": capec_stats.processed,
                "inserted": capec_stats.inserted,
                "updated": capec_stats.updated,
                "skipped": capec_stats.skipped,
            },
            provider="mitre",
            feed_kind="capec-bundle",
        )
        capec_stats.status = "ok"
    summary["patterns"] = capec_stats.as_dict()

    cwe_ref_stats = BootstrapStats(name="cwe_capec_refs", source_file=_relative_source(capec_path))
    capec_models = {
        obj.capec_id: obj
        for obj in await CapecAttackPatternIntel.all()
    }
    cwe_models = await CWEIntel.all()
    existing_cwe_capec = {
        (cwe_id, capec_id)
        for cwe_id, capec_id in await CWECAPECReference.all().values_list("cwe_id", "capec_id")
    }
    cwe_ref_creates: list[CWECAPECReference] = []
    for cwe in cwe_models:
        related_patterns = cwe.related_attack_patterns or []
        for capec_id in related_patterns:
            capec = capec_models.get(str(capec_id).upper())
            if not capec or (cwe.id, capec.id) in existing_cwe_capec:
                continue
            cwe_ref_creates.append(CWECAPECReference(cwe=cwe, capec=capec, source="cwe-xml"))
    if cwe_ref_creates:
        await CWECAPECReference.bulk_create(cwe_ref_creates, batch_size=500)
        cwe_ref_stats.inserted = len(cwe_ref_creates)
    cwe_ref_stats.processed = len(cwe_models)
    cwe_ref_stats.skipped = max(0, cwe_ref_stats.processed - cwe_ref_stats.inserted)
    cwe_ref_stats.status = "ok"
    summary["cwe_refs"] = cwe_ref_stats.as_dict()

    mitre_ref_stats = BootstrapStats(name="capec_mitre_refs", source_file=_relative_source(enterprise_path))
    if enterprise_path.exists():
        bundle_objects = _load_stix_objects(enterprise_path)
        mitre_refs: set[tuple[str, str]] = set()
        for obj in bundle_objects:
            if obj.get("type") != "attack-pattern":
                continue
            technique_id = _extract_external_id(obj, {"mitre-attack", "mobile-attack", "ics-attack"})
            if not technique_id:
                continue
            for capec_id in _extract_capec_ids_from_attack_pattern(obj):
                mitre_refs.add((capec_id, technique_id))
        mitre_ref_stats.processed = len(mitre_refs)
        technique_models = {
            obj.technique_id: obj
            for obj in await MitreTechniqueIntel.filter(technique_id__in=[technique_id for _, technique_id in mitre_refs]).all()
        } if mitre_refs else {}
        existing_capec_mitre = {
            (capec_id, technique_id)
            for capec_id, technique_id in await CAPECMitreTechniqueReference.all().values_list(
                "capec__capec_id", "technique__technique_id"
            )
        }
        ref_creates: list[CAPECMitreTechniqueReference] = []
        for capec_id, technique_id in mitre_refs:
            capec = capec_models.get(capec_id)
            technique = technique_models.get(technique_id)
            if not capec or not technique or (capec_id, technique_id) in existing_capec_mitre:
                continue
            ref_creates.append(
                CAPECMitreTechniqueReference(capec=capec, technique=technique, source="enterprise-attack-stix")
            )
        if ref_creates:
            await CAPECMitreTechniqueReference.bulk_create(ref_creates, batch_size=500)
            mitre_ref_stats.inserted = len(ref_creates)
        mitre_ref_stats.skipped = max(0, mitre_ref_stats.processed - mitre_ref_stats.inserted)
        mitre_ref_stats.status = "ok"
    else:
        mitre_ref_stats.status = "missing"
        mitre_ref_stats.errors = [f"Source file not found: {enterprise_path}"]
    summary["mitre_refs"] = mitre_ref_stats.as_dict()
    return summary


async def bootstrap_mitre_intelligence_async(force: bool = False) -> dict[str, Any]:
    intel_root = get_intelligence_root()
    mitre_dir = intel_root / "mitre"
    techniques_path = _latest_matching_file(mitre_dir, "techniques-*.json")
    actors_path = _latest_matching_file(mitre_dir, "threat-actors-*.json")
    enterprise_path = mitre_dir / "cti" / "enterprise-attack" / "enterprise-attack.json"

    summary = {
        "techniques": BootstrapStats(name="mitre_techniques", source_file=_relative_source(techniques_path) if techniques_path else None).as_dict(),
        "actors": BootstrapStats(name="mitre_actors", source_file=_relative_source(actors_path) if actors_path else None).as_dict(),
        "software": BootstrapStats(name="mitre_software", source_file=_relative_source(enterprise_path)).as_dict(),
    }

    if techniques_path and techniques_path.exists():
        tech_stats = BootstrapStats(name="mitre_techniques", source_file=_relative_source(techniques_path))
        snapshot_id, _existing_snapshot, is_current = await _snapshot_is_current(techniques_path, force=force)
        if is_current:
            tech_stats.status = "skipped"
            tech_stats.skipped = 1
        else:
            techniques: dict[str, dict[str, Any]] = {}
            for record in _iter_json_objects(techniques_path):
                technique_id = str(record.get("id") or record.get("technique_id") or "").strip()
                if not technique_id:
                    continue
                tactics = [str(value) for value in (record.get("tactics") or []) if value]
                techniques[technique_id] = {
                    "name": str(record.get("name") or "").strip(),
                    "description": record.get("description"),
                    "tactics": tactics,
                    "platforms": record.get("platforms") or [],
                    "data_sources": record.get("data_sources") or [],
                    "is_sub_technique": "." in technique_id,
                    "parent_technique_id": technique_id.split(".", 1)[0] if "." in technique_id else "",
                    "detection": record.get("detection"),
                    "mitigation_refs": record.get("mitigation_refs") or [],
                    "url": str(record.get("url") or _technique_url(technique_id)),
                    "source_file": _relative_source(techniques_path),
                    "raw_record": record,
                    "tags": record.get("tags") or [],
                }
            tech_stats.processed = len(techniques)
            existing = {
                obj.technique_id: obj
                for obj in await MitreTechniqueIntel.filter(technique_id__in=list(techniques.keys())).all()
            }
            forensic_existing = {
                obj.technique_id: obj
                for obj in await ForensicMITRETechnique.filter(technique_id__in=list(techniques.keys())).all()
            }
            techniques_to_create: list[MitreTechniqueIntel] = []
            forensic_to_create: list[ForensicMITRETechnique] = []
            for technique_id, defaults in techniques.items():
                current = existing.get(technique_id)
                if current:
                    if _apply_updates(current, defaults):
                        await current.save()
                        tech_stats.updated += 1
                    else:
                        tech_stats.skipped += 1
                else:
                    techniques_to_create.append(MitreTechniqueIntel(technique_id=technique_id, **defaults))

                forensic_defaults = {
                    "technique_name": defaults["name"],
                    "tactic": _map_tactic_name(defaults["tactics"]),
                    "sub_tactic": defaults["tactics"][1] if len(defaults["tactics"]) > 1 else "",
                    "technique_description": defaults["description"] or "",
                    "platforms": defaults["platforms"],
                    "data_sources": defaults["data_sources"],
                    "detection_notes": defaults["detection"] or "",
                    "mitigation_notes": "\n".join(defaults["mitigation_refs"]),
                    "references": [defaults["url"]] if defaults["url"] else [],
                }
                forensic = forensic_existing.get(technique_id)
                if forensic:
                    if _apply_updates(forensic, forensic_defaults):
                        await forensic.save()
                else:
                    forensic_to_create.append(ForensicMITRETechnique(technique_id=technique_id, **forensic_defaults))

            if techniques_to_create:
                await MitreTechniqueIntel.bulk_create(techniques_to_create, batch_size=500)
                tech_stats.inserted += len(techniques_to_create)
            if forensic_to_create:
                await ForensicMITRETechnique.bulk_create(forensic_to_create, batch_size=500)

            await _store_snapshot(
                techniques_path,
                snapshot_id,
                "mitre-techniques",
                {
                    "records": tech_stats.processed,
                    "inserted": tech_stats.inserted,
                    "updated": tech_stats.updated,
                    "skipped": tech_stats.skipped,
                },
            )
            tech_stats.status = "ok"
        summary["techniques"] = tech_stats.as_dict()

    if actors_path and actors_path.exists():
        actor_stats = BootstrapStats(name="mitre_actors", source_file=_relative_source(actors_path))
        snapshot_id, _existing_snapshot, is_current = await _snapshot_is_current(actors_path, force=force)
        if is_current:
            actor_stats.status = "skipped"
            actor_stats.skipped = 1
        else:
            actors: dict[str, dict[str, Any]] = {}
            actor_to_techniques: dict[str, list[str]] = {}
            for record in _iter_json_objects(actors_path):
                actor_name = str(record.get("name") or record.get("actor_name") or "").strip()
                if not actor_name:
                    continue
                description = record.get("description")
                actors[actor_name] = {
                    "description": description,
                    "aliases": record.get("aliases") or [],
                    "country_of_origin": str(record.get("country_of_origin") or "")[:3],
                    "motivation": str(record.get("motivation") or "")[:128],
                    "first_seen": _parse_datetime(record.get("first_seen")),
                    "last_seen": _parse_datetime(record.get("last_seen")),
                    "target_sectors": record.get("target_sectors") or [],
                    "target_regions": record.get("target_regions") or [],
                    "associated_groups": record.get("associated_groups") or [],
                    "tools_used": record.get("tools_used") or [],
                    "url": str(record.get("url") or _extract_group_url(description)),
                    "source_file": _relative_source(actors_path),
                    "raw_record": record,
                    "tags": record.get("tags") or [],
                }
                actor_to_techniques[actor_name] = _extract_technique_ids(description if isinstance(description, str) else None)
            actor_stats.processed = len(actors)
            existing = {
                obj.actor_name: obj
                for obj in await MitreThreatActorIntel.filter(actor_name__in=list(actors.keys())).all()
            }
            actors_to_create: list[MitreThreatActorIntel] = []
            for actor_name, defaults in actors.items():
                current = existing.get(actor_name)
                if current:
                    if _apply_updates(current, defaults):
                        await current.save()
                        actor_stats.updated += 1
                    else:
                        actor_stats.skipped += 1
                else:
                    actors_to_create.append(MitreThreatActorIntel(actor_name=actor_name, **defaults))
            if actors_to_create:
                await MitreThreatActorIntel.bulk_create(actors_to_create, batch_size=300)
                actor_stats.inserted += len(actors_to_create)

            all_actors: dict[str, MitreThreatActorIntel] = {
                obj.actor_name: obj
                for obj in await MitreThreatActorIntel.filter(actor_name__in=list(actors.keys())).all()
            }
            referenced_ids = sorted({tech_id for values in actor_to_techniques.values() for tech_id in values})
            if referenced_ids:
                technique_models = {
                    obj.technique_id: obj
                    for obj in await MitreTechniqueIntel.filter(technique_id__in=referenced_ids).all()
                }
                existing_ref_rows = await ThreatActorTechniqueReference.filter(
                        actor__actor_name__in=list(all_actors.keys()),
                        technique__technique_id__in=referenced_ids,
                    ).values_list("actor__actor_name", "technique__technique_id")
                existing_refs = {(actor_name, technique_id) for actor_name, technique_id in existing_ref_rows}
                ref_creates: list[ThreatActorTechniqueReference] = []
                for actor_name, technique_ids in actor_to_techniques.items():
                    actor = all_actors.get(actor_name)
                    if not actor:
                        continue
                    for technique_id in technique_ids:
                        technique = technique_models.get(technique_id)
                        if not technique or (actor_name, technique_id) in existing_refs:
                            continue
                        ref_creates.append(
                            ThreatActorTechniqueReference(
                                actor=actor,
                                technique=technique,
                                confidence=0.6,
                                evidence="Derived from actor description during bootstrap import.",
                            )
                        )
                if ref_creates:
                    await ThreatActorTechniqueReference.bulk_create(ref_creates, batch_size=500)

            await _store_snapshot(
                actors_path,
                snapshot_id,
                "mitre-actors",
                {
                    "records": actor_stats.processed,
                    "inserted": actor_stats.inserted,
                    "updated": actor_stats.updated,
                    "skipped": actor_stats.skipped,
                },
            )
            actor_stats.status = "ok"
        summary["actors"] = actor_stats.as_dict()

    software_stats = BootstrapStats(name="mitre_software", source_file=_relative_source(enterprise_path))
    if enterprise_path.exists():
        snapshot_id, _existing_snapshot, is_current = await _snapshot_is_current(enterprise_path, force=force)
        if is_current:
            software_stats.status = "skipped"
            software_stats.skipped = 1
        else:
            bundle_objects = _load_stix_objects(enterprise_path)
            software_by_stix_id: dict[str, dict[str, Any]] = {}
            actor_name_by_stix_id: dict[str, str] = {}
            technique_id_by_stix_id: dict[str, str] = {}
            actor_software_edges: set[tuple[str, str]] = set()
            software_technique_edges: set[tuple[str, str]] = set()

            for obj in bundle_objects:
                object_type = str(obj.get("type") or "")
                if object_type == "intrusion-set":
                    actor_name_by_stix_id[str(obj.get("id") or "")] = str(obj.get("name") or "").strip()
                elif object_type == "attack-pattern":
                    technique_id = _extract_external_id(obj, {"mitre-attack", "mobile-attack", "ics-attack"})
                    if technique_id:
                        technique_id_by_stix_id[str(obj.get("id") or "")] = technique_id
                elif object_type in {"malware", "tool"}:
                    software_id = _extract_external_id(obj, {"mitre-attack", "mobile-attack", "ics-attack"})
                    if not software_id:
                        continue
                    software_by_stix_id[str(obj.get("id") or "")] = {
                        "software_id": software_id,
                        "name": str(obj.get("name") or "").strip(),
                        "software_type": object_type,
                        "description": obj.get("description"),
                        "aliases": obj.get("x_mitre_aliases") or [],
                        "platforms": obj.get("x_mitre_platforms") or [],
                        "domains": obj.get("x_mitre_domains") or [],
                        "labels": obj.get("labels") or [],
                        "is_family": bool(obj.get("is_family", False)),
                        "vendor": str(obj.get("x_mitre_vendor") or ""),
                        "url": _extract_external_url(obj, {"mitre-attack", "mobile-attack", "ics-attack"}),
                        "source_file": _relative_source(enterprise_path),
                        "raw_record": obj,
                        "tags": [object_type, "mitre-family"],
                    }
                elif object_type == "relationship" and str(obj.get("relationship_type") or "") == "uses":
                    source_ref = str(obj.get("source_ref") or "")
                    target_ref = str(obj.get("target_ref") or "")
                    if source_ref.startswith("intrusion-set--") and target_ref.startswith(("malware--", "tool--")):
                        actor_name = actor_name_by_stix_id.get(source_ref)
                        software = software_by_stix_id.get(target_ref)
                        if actor_name and software:
                            actor_software_edges.add((actor_name, software["software_id"]))
                    elif source_ref.startswith(("malware--", "tool--")) and target_ref.startswith("attack-pattern--"):
                        software = software_by_stix_id.get(source_ref)
                        technique_id = technique_id_by_stix_id.get(target_ref)
                        if software and technique_id:
                            software_technique_edges.add((software["software_id"], technique_id))

            software_stats.processed = len(software_by_stix_id)
            existing = {
                obj.software_id: obj
                for obj in await MitreSoftwareFamilyIntel.filter(
                    software_id__in=[record["software_id"] for record in software_by_stix_id.values()]
                ).all()
            }
            software_to_create: list[MitreSoftwareFamilyIntel] = []
            for record in software_by_stix_id.values():
                software_id = record["software_id"]
                defaults = {k: v for k, v in record.items() if k != "software_id"}
                current = existing.get(software_id)
                if current:
                    if _apply_updates(current, defaults):
                        await current.save()
                        software_stats.updated += 1
                    else:
                        software_stats.skipped += 1
                else:
                    software_to_create.append(MitreSoftwareFamilyIntel(software_id=software_id, **defaults))
            if software_to_create:
                await MitreSoftwareFamilyIntel.bulk_create(software_to_create, batch_size=500)
                software_stats.inserted += len(software_to_create)

            software_models = {
                obj.software_id: obj
                for obj in await MitreSoftwareFamilyIntel.filter(
                    software_id__in=[record["software_id"] for record in software_by_stix_id.values()]
                ).all()
            }
            actor_models = {
                obj.actor_name: obj
                for obj in await MitreThreatActorIntel.filter(actor_name__in=[actor for actor, _ in actor_software_edges]).all()
            } if actor_software_edges else {}
            technique_models = {
                obj.technique_id: obj
                for obj in await MitreTechniqueIntel.filter(technique_id__in=[tech for _, tech in software_technique_edges]).all()
            } if software_technique_edges else {}

            existing_actor_software = {
                (actor_name, software_id)
                for actor_name, software_id in await ThreatActorSoftwareReference.all().values_list(
                    "actor__actor_name", "software__software_id"
                )
            }
            existing_software_technique = {
                (software_id, technique_id)
                for software_id, technique_id in await SoftwareTechniqueReference.all().values_list(
                    "software__software_id", "technique__technique_id"
                )
            }

            actor_software_creates: list[ThreatActorSoftwareReference] = []
            for actor_name, software_id in actor_software_edges:
                actor = actor_models.get(actor_name)
                software = software_models.get(software_id)
                if not actor or not software or (actor_name, software_id) in existing_actor_software:
                    continue
                actor_software_creates.append(
                    ThreatActorSoftwareReference(
                        actor=actor,
                        software=software,
                        relationship_type="uses",
                        confidence=0.8,
                        evidence="Derived from MITRE enterprise-attack relationship bundle.",
                    )
                )
            if actor_software_creates:
                await ThreatActorSoftwareReference.bulk_create(actor_software_creates, batch_size=500)

            software_technique_creates: list[SoftwareTechniqueReference] = []
            for software_id, technique_id in software_technique_edges:
                software = software_models.get(software_id)
                technique = technique_models.get(technique_id)
                if not software or not technique or (software_id, technique_id) in existing_software_technique:
                    continue
                software_technique_creates.append(
                    SoftwareTechniqueReference(
                        software=software,
                        technique=technique,
                        relationship_type="uses",
                        confidence=0.8,
                        evidence="Derived from MITRE enterprise-attack relationship bundle.",
                    )
                )
            if software_technique_creates:
                await SoftwareTechniqueReference.bulk_create(software_technique_creates, batch_size=500)

            await _store_snapshot(
                enterprise_path,
                snapshot_id,
                "mitre-software",
                {
                    "records": software_stats.processed,
                    "inserted": software_stats.inserted,
                    "updated": software_stats.updated,
                    "skipped": software_stats.skipped,
                    "actor_software_edges": len(actor_software_edges),
                    "software_technique_edges": len(software_technique_edges),
                },
                provider="mitre",
                feed_kind="enterprise-attack-stix",
                source_url="https://github.com/mitre/cti",
            )
            software_stats.status = "ok"
    else:
        software_stats.status = "missing"
        software_stats.errors = [f"Source file not found: {enterprise_path}"]
    summary["software"] = software_stats.as_dict()

    return summary


async def bootstrap_misp_intelligence_async(force: bool = False) -> dict[str, Any]:
    intel_root = get_intelligence_root()
    feeds_dir = intel_root / "feeds"
    feed_files = sorted(path for path in feeds_dir.glob("misp-*.json") if path.is_file()) if feeds_dir.exists() else []
    summary = {
        "events": BootstrapStats(name="misp_events", source_file=_relative_source(feeds_dir / "misp-*.json")).as_dict(),
        "attributes": BootstrapStats(name="misp_attributes", source_file=_relative_source(feeds_dir / "misp-*.json")).as_dict(),
        "ioc_db": BootstrapStats(name="misp_ioc_db", source_file=_relative_source(feeds_dir / "misp-*.json")).as_dict(),
    }
    if not feed_files:
        for component in summary.values():
            component["status"] = "missing"
            component["errors"] = [f"No MISP feed snapshots found in: {feeds_dir}"]
        return summary

    event_stats = BootstrapStats(name="misp_events", source_file=_relative_source(feed_files[-1]))
    attribute_stats = BootstrapStats(name="misp_attributes", source_file=_relative_source(feed_files[-1]))
    ioc_stats = BootstrapStats(name="misp_ioc_db", source_file=_relative_source(feed_files[-1]))

    for path in feed_files:
        payload = _read_json_document(path)
        snapshot_id, _existing_snapshot, is_current = await _snapshot_is_current(path, force=force)
        if is_current:
            event_stats.skipped += 1
            attribute_stats.skipped += 1
            ioc_stats.skipped += 1
            continue

        await _store_snapshot(
            path,
            snapshot_id,
            "misp",
            _snapshot_payload(payload),
            provider="misp",
            feed_kind="event_export",
        )
        snapshot = await ThreatIntelFeedSnapshot.get_or_none(source_file=_relative_source(path))
        events = _extract_misp_events(payload)
        event_stats.processed += len(events)

        event_defaults_by_uuid: dict[str, dict[str, Any]] = {}
        attributes_by_uuid: dict[str, dict[str, Any]] = {}
        canonical_iocs: list[dict[str, Any]] = []

        for event in events:
            event_uuid = str(event.get("uuid") or event.get("id") or "").strip()
            if not event_uuid:
                continue
            tags = _extract_tag_names(event.get("Tag") or event.get("tags") or [])
            event_defaults_by_uuid[event_uuid] = {
                "event_id": str(event.get("id") or "").strip() or None,
                "info": str(event.get("info") or event.get("title") or "").strip(),
                "analysis": str(event.get("analysis") or "").strip(),
                "threat_level": str(event.get("threat_level_id") or event.get("threat_level") or "").strip(),
                "distribution": str(event.get("distribution") or "").strip(),
                "published": _normalize_bool(event.get("published")),
                "orgc_name": str((event.get("Orgc") or {}).get("name") or event.get("orgc_name") or "").strip(),
                "org_name": str((event.get("Org") or {}).get("name") or event.get("org_name") or "").strip(),
                "tags": tags,
                "attribute_count": len(_extract_misp_attributes(event)),
                "first_seen": _parse_datetime(event.get("date") or event.get("publish_timestamp") or event.get("timestamp")),
                "last_seen": _parse_datetime(event.get("timestamp") or event.get("publish_timestamp")),
                "published_at": _parse_datetime(event.get("publish_timestamp") or event.get("date")),
                "source_file": _relative_source(path),
                "source_snapshot": snapshot,
                "raw_record": event,
            }

            for attribute in _extract_misp_attributes(event):
                attribute_uuid = _misp_attribute_uuid(event_uuid, attribute)
                category = str(attribute.get("category") or "").strip()
                attribute_type = str(attribute.get("type") or "").strip()
                value_text = str(attribute.get("value") or "").strip()
                normalized_ioc_type = _normalize_ioc_type(attribute_type, category, value_text)
                attribute_tags = _extract_tag_names(attribute.get("Tag") or attribute.get("tags") or [])
                attributes_by_uuid[attribute_uuid] = {
                    "event_uuid": event_uuid,
                    "defaults": {
                        "attribute_id": str(attribute.get("id") or "").strip() or None,
                        "category": category,
                        "attribute_type": attribute_type,
                        "normalized_ioc_type": normalized_ioc_type,
                        "value": value_text,
                        "comment": attribute.get("comment"),
                        "to_ids": _normalize_bool(attribute.get("to_ids")),
                        "deleted": _normalize_bool(attribute.get("deleted")),
                        "distribution": str(attribute.get("distribution") or event.get("distribution") or "").strip(),
                        "first_seen": _parse_datetime(attribute.get("first_seen") or attribute.get("timestamp") or event.get("date")),
                        "last_seen": _parse_datetime(attribute.get("last_seen") or attribute.get("timestamp") or event.get("timestamp")),
                        "tags": _dedupe_strings(tags + attribute_tags),
                        "source_file": _relative_source(path),
                        "source_snapshot": snapshot,
                        "raw_record": attribute,
                    },
                }
                if value_text and not _normalize_bool(attribute.get("deleted")):
                    canonical_iocs.append(
                        {
                            "ioc_type": normalized_ioc_type,
                            "value": value_text,
                            "confidence": "high" if _normalize_bool(attribute.get("to_ids")) else "medium",
                            "tags": _dedupe_strings(tags + attribute_tags + ["misp", category]),
                            "context": attribute.get("comment") or event.get("info") or category,
                            "first_seen": attribute.get("first_seen") or attribute.get("timestamp") or event.get("date"),
                            "last_seen": attribute.get("last_seen") or attribute.get("timestamp") or event.get("timestamp"),
                            "source_file": _relative_source(path),
                            "raw_record": {
                                "provider": "misp",
                                "event_uuid": event_uuid,
                                "attribute_uuid": attribute_uuid,
                                "event_info": event.get("info"),
                                "attribute": attribute,
                            },
                        }
                    )

        existing_events = {
            row.event_uuid: row
            for row in await MISPEventIntel.filter(event_uuid__in=list(event_defaults_by_uuid.keys())).all()
        } if event_defaults_by_uuid else {}
        event_creates: list[MISPEventIntel] = []
        for event_uuid, defaults in event_defaults_by_uuid.items():
            current = existing_events.get(event_uuid)
            if current:
                if _apply_updates(current, defaults):
                    await current.save()
                    event_stats.updated += 1
                else:
                    event_stats.skipped += 1
            else:
                event_creates.append(MISPEventIntel(event_uuid=event_uuid, **defaults))
        if event_creates:
            await MISPEventIntel.bulk_create(event_creates, batch_size=300)
            event_stats.inserted += len(event_creates)

        event_models = {
            row.event_uuid: row
            for row in await MISPEventIntel.filter(event_uuid__in=list(event_defaults_by_uuid.keys())).all()
        } if event_defaults_by_uuid else {}

        attribute_stats.processed += len(attributes_by_uuid)
        existing_attributes = {
            row.attribute_uuid: row
            for row in await MISPAttributeIntel.filter(attribute_uuid__in=list(attributes_by_uuid.keys())).all()
        } if attributes_by_uuid else {}
        attribute_creates: list[MISPAttributeIntel] = []
        for attribute_uuid, payload_record in attributes_by_uuid.items():
            event_model = event_models.get(payload_record["event_uuid"])
            if not event_model:
                continue
            defaults = {**payload_record["defaults"], "event": event_model}
            current = existing_attributes.get(attribute_uuid)
            if current:
                if _apply_updates(current, defaults):
                    await current.save()
                    attribute_stats.updated += 1
                else:
                    attribute_stats.skipped += 1
            else:
                attribute_creates.append(MISPAttributeIntel(attribute_uuid=attribute_uuid, **defaults))
        if attribute_creates:
            await MISPAttributeIntel.bulk_create(attribute_creates, batch_size=500)
            attribute_stats.inserted += len(attribute_creates)

        ioc_result = await _upsert_ioc_database_entries(canonical_iocs)
        ioc_stats.processed += ioc_result["processed"]
        ioc_stats.inserted += ioc_result["inserted"]
        ioc_stats.updated += ioc_result["updated"]
        ioc_stats.skipped += ioc_result["skipped"]

    event_stats.status = "ok"
    attribute_stats.status = "ok"
    ioc_stats.status = "ok"
    summary["events"] = event_stats.as_dict()
    summary["attributes"] = attribute_stats.as_dict()
    summary["ioc_db"] = ioc_stats.as_dict()
    return summary


async def bootstrap_opencti_intelligence_async(force: bool = False) -> dict[str, Any]:
    intel_root = get_intelligence_root()
    feeds_dir = intel_root / "feeds"
    feed_files = sorted(path for path in feeds_dir.glob("opencti-*.json") if path.is_file()) if feeds_dir.exists() else []
    summary = {
        "indicators": BootstrapStats(name="opencti_indicators", source_file=_relative_source(feeds_dir / "opencti-*.json")).as_dict(),
        "entities": BootstrapStats(name="opencti_entities", source_file=_relative_source(feeds_dir / "opencti-*.json")).as_dict(),
        "ioc_db": BootstrapStats(name="opencti_ioc_db", source_file=_relative_source(feeds_dir / "opencti-*.json")).as_dict(),
        "threat_profiles": BootstrapStats(name="opencti_threat_profiles", source_file=_relative_source(feeds_dir / "opencti-*.json")).as_dict(),
    }
    if not feed_files:
        for component in summary.values():
            component["status"] = "missing"
            component["errors"] = [f"No OpenCTI feed snapshots found in: {feeds_dir}"]
        return summary

    indicator_stats = BootstrapStats(name="opencti_indicators", source_file=_relative_source(feed_files[-1]))
    entity_stats = BootstrapStats(name="opencti_entities", source_file=_relative_source(feed_files[-1]))
    ioc_stats = BootstrapStats(name="opencti_ioc_db", source_file=_relative_source(feed_files[-1]))
    profile_stats = BootstrapStats(name="opencti_threat_profiles", source_file=_relative_source(feed_files[-1]))

    actor_models = await MitreThreatActorIntel.all()
    actor_by_name = {actor.actor_name.casefold(): actor for actor in actor_models}
    for actor in actor_models:
        for alias in actor.aliases or []:
            await actor_by_name.setdefault(str(alias).casefold(), actor)

    for path in feed_files:
        payload = _read_json_document(path)
        snapshot_id, _existing_snapshot, is_current = await _snapshot_is_current(path, force=force)
        if is_current:
            indicator_stats.skipped += 1
            entity_stats.skipped += 1
            ioc_stats.skipped += 1
            profile_stats.skipped += 1
            continue

        await _store_snapshot(
            path,
            snapshot_id,
            "opencti",
            _snapshot_payload(payload),
            provider="opencti",
            feed_kind="export",
        )
        snapshot = await ThreatIntelFeedSnapshot.get_or_none(source_file=_relative_source(path))
        objects = _extract_opencti_objects(payload)

        indicator_defaults_by_id: dict[str, dict[str, Any]] = {}
        entity_defaults_by_id: dict[str, dict[str, Any]] = {}
        canonical_iocs: list[dict[str, Any]] = []
        threat_profiles: list[dict[str, Any]] = []

        for obj in objects:
            object_type = str(obj.get("type") or obj.get("entity_type") or obj.get("x_opencti_type") or "").strip().lower()
            stix_id = str(obj.get("standard_id") or obj.get("id") or "").strip()
            if not stix_id:
                continue
            labels = _extract_opencti_labels(obj)
            created_by = _extract_opencti_created_by(obj)
            external_references = _extract_opencti_external_references(obj)
            if object_type == "indicator":
                pattern = str(obj.get("pattern") or "").strip()
                observable_values = _extract_opencti_observable_values(pattern)
                indicator_types = _dedupe_strings(obj.get("indicator_types") or obj.get("x_opencti_indicator_types") or [])
                indicator_defaults_by_id[stix_id] = {
                    "name": str(obj.get("name") or "").strip(),
                    "description": obj.get("description"),
                    "pattern": pattern,
                    "pattern_type": str(obj.get("pattern_type") or "stix").strip(),
                    "indicator_types": indicator_types,
                    "observable_values": observable_values,
                    "confidence": _safe_int(obj.get("confidence")),
                    "score": _safe_float(obj.get("x_opencti_score")),
                    "valid_from": _parse_datetime(obj.get("valid_from")),
                    "valid_until": _parse_datetime(obj.get("valid_until")),
                    "labels": labels,
                    "created_by": created_by,
                    "revoked": _normalize_bool(obj.get("revoked")),
                    "source_file": _relative_source(path),
                    "source_snapshot": snapshot,
                    "raw_record": obj,
                }
                normalized_ioc_type = _normalize_ioc_type(indicator_types[0] if indicator_types else "", object_type, observable_values[0] if observable_values else "")
                for observable_value in observable_values:
                    canonical_iocs.append(
                        {
                            "ioc_type": _normalize_ioc_type(normalized_ioc_type, object_type, observable_value),
                            "value": observable_value,
                            "confidence": _pick_confidence(obj.get("x_opencti_score"), obj.get("confidence")),
                            "tags": _dedupe_strings(labels + indicator_types + ["opencti"]),
                            "context": pattern,
                            "first_seen": obj.get("valid_from") or obj.get("created"),
                            "last_seen": obj.get("modified") or obj.get("valid_until") or obj.get("updated_at"),
                            "source_file": _relative_source(path),
                            "raw_record": {
                                "provider": "opencti",
                                "indicator_id": stix_id,
                                "pattern": pattern,
                                "record": obj,
                            },
                        }
                    )
            else:
                entity_defaults_by_id[stix_id] = {
                    "entity_type": object_type or "entity",
                    "name": str(obj.get("name") or "").strip(),
                    "description": obj.get("description"),
                    "aliases": _dedupe_strings(obj.get("aliases") or obj.get("x_opencti_aliases") or obj.get("x_mitre_aliases") or []),
                    "labels": labels,
                    "confidence": _safe_int(obj.get("confidence")),
                    "first_seen": _parse_datetime(obj.get("first_seen") or obj.get("created")),
                    "last_seen": _parse_datetime(obj.get("last_seen") or obj.get("modified")),
                    "created_by": created_by,
                    "external_references": external_references,
                    "source_file": _relative_source(path),
                    "source_snapshot": snapshot,
                    "raw_record": obj,
                }
                if object_type in {"threat-actor", "intrusion-set"} and entity_defaults_by_id[stix_id]["name"]:
                    name = entity_defaults_by_id[stix_id]["name"]
                    actor = actor_by_name.get(name.casefold())
                    confidence_value = _safe_float(obj.get("confidence"))
                    threat_profiles.append(
                        {
                            "profile_name": name,
                            "actor": actor,
                            "summary": obj.get("description"),
                            "motivations": _dedupe_strings(
                                [obj.get("primary_motivation")] + (obj.get("secondary_motivations") or []) + labels
                            ),
                            "sectors": _dedupe_strings(obj.get("goals") or obj.get("sectors") or []),
                            "regions": _dedupe_strings(obj.get("locations") or obj.get("regions") or []),
                            "ttps": _dedupe_strings(
                                _extract_technique_ids(obj.get("description"))
                                + _extract_attack_ids_from_external_references(external_references)
                            ),
                            "confidence_score": confidence_value / 100.0 if confidence_value is not None else None,
                            "source_file": _relative_source(path),
                            "raw_record": {
                                "provider": "opencti",
                                "entity_id": stix_id,
                                "record": obj,
                            },
                        }
                    )

        indicator_stats.processed += len(indicator_defaults_by_id)
        existing_indicators = {
            row.stix_id: row
            for row in await OpenCTIIndicatorIntel.filter(stix_id__in=list(indicator_defaults_by_id.keys())).all()
        } if indicator_defaults_by_id else {}
        indicator_creates: list[OpenCTIIndicatorIntel] = []
        for stix_id, defaults in indicator_defaults_by_id.items():
            current = existing_indicators.get(stix_id)
            if current:
                if _apply_updates(current, defaults):
                    await current.save()
                    indicator_stats.updated += 1
                else:
                    indicator_stats.skipped += 1
            else:
                indicator_creates.append(OpenCTIIndicatorIntel(stix_id=stix_id, **defaults))
        if indicator_creates:
            await OpenCTIIndicatorIntel.bulk_create(indicator_creates, batch_size=300)
            indicator_stats.inserted += len(indicator_creates)

        entity_stats.processed += len(entity_defaults_by_id)
        existing_entities = {
            row.stix_id: row
            for row in await OpenCTIEntityIntel.filter(stix_id__in=list(entity_defaults_by_id.keys())).all()
        } if entity_defaults_by_id else {}
        entity_creates: list[OpenCTIEntityIntel] = []
        for stix_id, defaults in entity_defaults_by_id.items():
            current = existing_entities.get(stix_id)
            if current:
                if _apply_updates(current, defaults):
                    await current.save()
                    entity_stats.updated += 1
                else:
                    entity_stats.skipped += 1
            else:
                entity_creates.append(OpenCTIEntityIntel(stix_id=stix_id, **defaults))
        if entity_creates:
            await OpenCTIEntityIntel.bulk_create(entity_creates, batch_size=300)
            entity_stats.inserted += len(entity_creates)

        ioc_result = await _upsert_ioc_database_entries(canonical_iocs)
        ioc_stats.processed += ioc_result["processed"]
        ioc_stats.inserted += ioc_result["inserted"]
        ioc_stats.updated += ioc_result["updated"]
        ioc_stats.skipped += ioc_result["skipped"]

        profile_result = await _upsert_threat_profile_entries(threat_profiles)
        profile_stats.processed += profile_result["processed"]
        profile_stats.inserted += profile_result["inserted"]
        profile_stats.updated += profile_result["updated"]
        profile_stats.skipped += profile_result["skipped"]

    indicator_stats.status = "ok"
    entity_stats.status = "ok"
    ioc_stats.status = "ok"
    profile_stats.status = "ok"
    summary["indicators"] = indicator_stats.as_dict()
    summary["entities"] = entity_stats.as_dict()
    summary["ioc_db"] = ioc_stats.as_dict()
    summary["threat_profiles"] = profile_stats.as_dict()
    return summary


async def bootstrap_feed_snapshots_async(force: bool = False) -> dict[str, Any]:
    intel_root = get_intelligence_root()
    feeds_dir = intel_root / "feeds"
    stats = BootstrapStats(name="feed_snapshots", source_file=_relative_source(feeds_dir))
    if not feeds_dir.exists():
        stats.status = "missing"
        stats.errors = [f"Feed directory not found: {feeds_dir}"]
        return stats.as_dict()

    feed_files = sorted(path for path in feeds_dir.iterdir() if path.is_file())
    stats.processed = len(feed_files)
    for path in feed_files:
        snapshot_id, _existing_snapshot, is_current = await _snapshot_is_current(path, force=force)
        if is_current:
            stats.skipped += 1
            continue
        try:
            raw_text = path.read_text(encoding="utf-8", errors="ignore")
            payload: Any = json.loads(raw_text)
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            payload = {"raw_text": path.read_text(encoding="utf-8", errors="ignore")[:10000]}
        metadata = _classify_feed_snapshot(path, payload)
        feed_name = path.name.split("-", 1)[0]
        existing = await ThreatIntelFeedSnapshot.get_or_none(source_file=_relative_source(path))
        if existing:
            existing.provider = metadata["provider"]
            existing.feed_name = feed_name
            existing.feed_kind = metadata["feed_kind"]
            existing.snapshot_id = snapshot_id
            existing.source_url = metadata["source_url"]
            existing.record_count = metadata["record_count"]
            existing.payload = payload
            await existing.save()
            stats.updated += 1
        else:
            await ThreatIntelFeedSnapshot.create(
                provider=metadata["provider"],
                feed_name=feed_name,
                feed_kind=metadata["feed_kind"],
                snapshot_id=snapshot_id,
                source_file=_relative_source(path),
                source_url=metadata["source_url"],
                record_count=metadata["record_count"],
                payload=payload,
            )
            stats.inserted += 1
    stats.status = "ok"
    return stats.as_dict()


async def bootstrap_update_log_async(force: bool = False) -> dict[str, Any]:
    intel_root = get_intelligence_root()
    source_path = intel_root / "update-log.md"
    stats = BootstrapStats(name="update_log", source_file=_relative_source(source_path))
    if not source_path.exists():
        stats.status = "missing"
        stats.errors = [f"Source file not found: {source_path}"]
        return stats.as_dict()

    snapshot_id, _existing_snapshot, is_current = await _snapshot_is_current(source_path, force=force)
    if is_current:
        stats.status = "skipped"
        stats.skipped = 1
        return stats.as_dict()

    lines = source_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    parsed_entries: list[IntelligenceUpdateLogEntry] = []
    await IntelligenceUpdateLogEntry.filter(source_file=_relative_source(source_path)).delete()
    for index, line in enumerate(lines, start=1):
        match = _UPDATE_LOG_PATTERN.match(line.strip())
        if not match:
            continue
        parsed_entries.append(
            IntelligenceUpdateLogEntry(
                run_id=match.group("run_id").strip(),
                category=match.group("category").strip(),
                status=match.group("status").strip(),
                message=match.group("message").strip(),
                line_number=index,
                source_file=_relative_source(source_path),
            )
        )
    if parsed_entries:
        await IntelligenceUpdateLogEntry.bulk_create(parsed_entries, batch_size=500)
    stats.processed = len(lines)
    stats.inserted = len(parsed_entries)
    await _store_snapshot(
        source_path,
        snapshot_id,
        "update-log",
        {"records": stats.inserted},
    )
    stats.status = "ok"
    return stats.as_dict()


async def bootstrap_intelligence_async(force: bool = False, include_feeds: bool = True) -> dict[str, Any]:
    """Bootstrap canonical threat intelligence tables from shared project sources."""
    if get_current_context() is None:
        raise RuntimeError("Tortoise ORM is not initialized")

    cve = await bootstrap_cve_intelligence_async(force=force)
    cwe = await bootstrap_cwe_intelligence_async(force=force)
    capec = await bootstrap_capec_intelligence_async(force=force)
    mitre = await bootstrap_mitre_intelligence_async(force=force)
    misp = await bootstrap_misp_intelligence_async(force=force)
    opencti = await bootstrap_opencti_intelligence_async(force=force)
    update_log = await bootstrap_update_log_async(force=force)
    feeds = await bootstrap_feed_snapshots_async(force=force) if include_feeds else {
        "name": "feed_snapshots",
        "status": "skipped",
        "processed": 0,
        "inserted": 0,
        "updated": 0,
        "skipped": 0,
        "errors": [],
        "source_file": _relative_source(get_intelligence_root() / "feeds"),
    }

    return {
        "status": "ok",
        "intel_root": str(get_intelligence_root()),
        "force": force,
        "include_feeds": include_feeds,
        "components": {
            "cve": cve,
            "cwe": cwe,
            "capec": capec,
            "mitre": mitre,
            "misp": misp,
            "opencti": opencti,
            "update_log": update_log,
            "feeds": feeds,
        },
    }

