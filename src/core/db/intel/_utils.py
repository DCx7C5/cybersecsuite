

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

from utils.deduplication import deduplicate_strings, deduplicate_items

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_INTEL_DIR = _PROJECT_ROOT / "data" / "cybersec-shared" / "intelligence"
_JSON_DECODER = json.JSONDecoder()
_UPDATE_LOG_PATTERN = re.compile(r"^\[(?P<run_id>[^]]+)]\s+(?P<category>[^:]+):\s+(?P<status>[^-]+)-\s+(?P<message>.+)$")
_ATTACK_GROUP_RE = re
_ATTACK_TECHNIQUE_RE = re.compile(r"https?://attack\.mitre\.org/techniques/(?P<path>T\d{4}(?:/\d{3})?)/?")
_CAPEC_EXTERNAL_ID_RE = re.compile(r"CAPEC-\d+")
_STIX_PATTERN_VALUE_RE = re.compile(r"=\s*(?:'([^']+)'|\"([^\"]+)\")")


def _relative_source(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(_PROJECT_ROOT))
    except ValueError:
        return str(path.resolve())


def _snapshot_id(path: Path) -> str:
    stat = path.stat()
    payload = f"{path.resolve()}:{stat.st_size}:{stat.st_mtime_ns}".encode("utf-8")
    return hashlib.sha1(payload).hexdigest()[:20]


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
    return deduplicate_items(capec_ids)


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
    """
    Remove duplicate strings while preserving order.

    Delegates to utils.deduplication.deduplicate_strings() for consolidated logic.
    Kept here for backward compatibility with internal db.intel imports.

    Args:
        values: Iterable of values to deduplicate

    Returns:
        List of unique strings in order of first appearance
    """
    return deduplicate_strings(values)


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


def _apply_updates(obj: Any, defaults: dict[str, Any]) -> bool:
    changed = False
    for field_name, new_value in defaults.items():
        if getattr(obj, field_name) != new_value:
            setattr(obj, field_name, new_value)
            changed = True
    return changed


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
