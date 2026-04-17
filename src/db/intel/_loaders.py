"""Feed parsers and MITRE helpers — MISP, OpenCTI, STIX, CWE XML, MITRE ATT&CK."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree

from db.models.enums import MITRETactic
from db.intel._utils import (
    _ATTACK_GROUP_RE,
    _STIX_PATTERN_VALUE_RE,
    _dedupe_strings,
    _extract_tag_names,
)


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
        object_key = str(
            obj.get("standard_id") or obj.get("id") or f"{obj.get('type')}:{obj.get('name')}:{len(deduped)}"
        )
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
        mitigation_values = [text for text in record['mitigations'] if isinstance(text, str)]
        record["mitigations"] = list(dict.fromkeys(text for text in mitigation_values if text))
        records[f"CWE-{cwe_id}"] = record
        elem.clear()
    return records


def _map_tactic_name(values: list[str]) -> MITRETactic:
    for value in values:
        normalized: str = value.strip().replace("-", "_").replace(" ", "_").upper()
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
