#!/usr/bin/env python3
"""
IOCDiscovered Hook — fires when an IOC is identified.
Logs to iocs.md, cross-references MITRE, and appends to session timeline.
"""
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _utils import ensure_structure, get_session_dir, audit, append_file, emit, hook_context, read_stdin, SEVERITY_EMOJI

MITRE_BY_IOC_TYPE = {
    "ip":          ["T1071 - Application Layer Protocol", "T1095 - Non-Application Layer Protocol"],
    "domain":      ["T1568 - Dynamic Resolution", "T1071.004 - DNS"],
    "hash":        ["T1027 - Obfuscated Files", "T1036 - Masquerading"],
    "url":         ["T1071.001 - Web Protocols", "T1189 - Drive-by Compromise"],
    "email":       ["T1566 - Phishing", "T1598 - Spearphishing for Info"],
    "file_path":   ["T1036 - Masquerading", "T1083 - File Discovery"],
    "registry":    ["T1112 - Modify Registry", "T1547 - Boot Autostart"],
    "yara":        ["T1027 - Obfuscated Files", "T1055 - Process Injection"],
    "cve":         ["T1190 - Exploit Public-Facing App", "T1203 - Exploitation for Client Execution"],
    "certificate": ["T1588.004 - Digital Certificates", "T1553 - Subvert Trust Controls"],
}

async def main():
    ensure_structure()
    data = read_stdin()

    ioc_value    = data.get("ioc") or data.get("value", "unknown")
    ioc_type     = (data.get("type") or data.get("ioc_type", "unknown")).lower()
    severity     = data.get("severity", "medium").lower()
    source       = data.get("source", "detection")
    context_text = data.get("context", "")
    agent_name   = data.get("agent_name", os.environ.get("CYBERSEC_AGENT_NAME", "unknown"))

    session_dir = get_session_dir()
    now         = datetime.now(timezone.utc)
    ioc_id      = f"IOC-{now.strftime('%Y%m%d%H%M%S')}"
    emoji       = SEVERITY_EMOJI.get(severity, "🟡")

    mitre = MITRE_BY_IOC_TYPE.get(ioc_type, ["T1071 - Application Layer Protocol"])

    if session_dir:
        # iocs.md table row
        ioc_row = (
            f"| `{ioc_value}` | {ioc_type} | {severity.upper()} | {agent_name} "
            f"| {now.strftime('%H:%M:%S')} | {source} |\n"
        )
        iocs_path = session_dir / "iocs.md"
        if not iocs_path.exists():
            append_file(iocs_path, "| IOC | Type | Severity | Agent | Time | Source |\n|-----|------|----------|-------|------|--------|\n")
        append_file(iocs_path, ioc_row)

        # Detailed IOC record
        ioc_dir = session_dir / "iocs"
        ioc_dir.mkdir(exist_ok=True)
        record = {
            "ioc_id":   ioc_id,
            "value":    ioc_value,
            "type":     ioc_type,
            "severity": severity,
            "source":   source,
            "agent":    agent_name,
            "ts":       now.isoformat(),
            "context":  context_text,
            "mitre":    mitre,
        }
        (ioc_dir / f"{ioc_id}.json").write_text(json.dumps(record, indent=2))

        # Timeline
        append_file(
            session_dir / "timeline.md",
            f"| {now.strftime('%H:%M:%S')} | ioc_discovered | {ioc_type} | `{ioc_value[:40]}` severity={severity} |\n"
        )

    audit({"event": "IOCDiscovered", "ioc": ioc_value, "type": ioc_type, "severity": severity})

    mitre_fmt = "\n".join(f"• {t}" for t in mitre)
    emit(hook_context(
        f"{emoji} **IOC DISCOVERED** — {ioc_type.upper()} [{severity.upper()}]\n\n"
        f"**ID:** `{ioc_id}`\n"
        f"**Value:** `{ioc_value}`\n"
        f"**Source:** {source}\n"
        f"**Agent:** {agent_name}\n"
        f"**Time:** {now.strftime('%H:%M:%S UTC')}\n\n"
        f"**MITRE ATT&CK:**\n{mitre_fmt}\n"
        + (f"\n**Context:** {context_text}" if context_text else "")
    ))


if __name__ == "__main__":
    asyncio.run(main())

