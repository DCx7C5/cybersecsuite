#!/usr/bin/env python3
"""
EvidenceCollected Hook — fires when digital evidence is collected.
Computes BLAKE2b integrity hash, updates chain of custody, logs to session.
"""
import asyncio
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _utils import ensure_structure, get_session_dir, audit, append_file, emit, hook_context, read_stdin

PRIORITY_TYPES = {"memory_dump", "binary_file", "malware_sample", "core_dump"}
MEDIUM_TYPES   = {"log_file", "configuration_file", "network_capture", "pcap"}


def _blake2b_file(path: Path) -> str | None:
    try:
        h = hashlib.blake2b(digest_size=32)
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


async def main():
    ensure_structure()
    data = read_stdin()

    evidence_path   = Path(data.get("evidence_path") or os.environ.get("CYBERSEC_EVIDENCE_PATH", "unknown"))
    evidence_type   = data.get("evidence_type", "digital_evidence")
    collection_method = data.get("collection_method", "manual")
    investigation_id  = data.get("investigation_id") or os.environ.get("CYBERSEC_INVESTIGATION_ID", "unknown")
    agent_name      = data.get("agent_name", os.environ.get("CYBERSEC_AGENT_NAME", "unknown"))

    session_dir = get_session_dir()
    now         = datetime.now(timezone.utc)
    evidence_id = f"EVID-{now.strftime('%Y%m%d%H%M%S')}"

    # Priority
    if evidence_type in PRIORITY_TYPES:
        priority = "HIGH"
    elif evidence_type in MEDIUM_TYPES:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    # Integrity hash (BLAKE2b — consistent with crypto stack)
    file_hash = None
    file_size = None
    if evidence_path.exists() and evidence_path.is_file():
        loop = asyncio.get_running_loop()
        file_hash = await loop.run_in_executor(None, _blake2b_file, evidence_path)
        file_size = evidence_path.stat().st_size

    record = {
        "evidence_id":       evidence_id,
        "source_path":       str(evidence_path),
        "evidence_type":     evidence_type,
        "collection_method": collection_method,
        "investigation_id":  investigation_id,
        "collected_by":      agent_name,
        "collection_time":   now.isoformat(),
        "priority":          priority,
        "integrity": {
            "algorithm": "blake2b-256",
            "hash":      file_hash,
            "file_size": file_size,
            "verified":  file_hash is not None,
        },
        "chain_of_custody": {
            "collector":   agent_name,
            "timestamp":   now.isoformat(),
            "method":      collection_method,
            "transfers":   [],
        },
    }

    if session_dir:
        inv_dir  = session_dir / investigation_id
        evid_dir = inv_dir / "evidence"
        evid_dir.mkdir(parents=True, exist_ok=True)

        # Save record
        (evid_dir / f"{evidence_id}.json").write_text(json.dumps(record, indent=2))

        # Preserve file copy
        if evidence_path.exists() and evidence_path.is_file():
            dest = evid_dir / f"{evidence_id}_{evidence_path.name}"
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, shutil.copy2, str(evidence_path), str(dest))

        # artifacts.md
        append_file(
            session_dir / "artifacts.md",
            f"- `{evidence_id}` | {evidence_type} | {priority} | blake2b=`{(file_hash or 'N/A')[:16]}…`\n"
        )

        # Timeline
        append_file(
            session_dir / "timeline.md",
            f"| {now.strftime('%H:%M:%S')} | evidence_collected | {evidence_type} | {priority} | `{evidence_id}` |\n"
        )

    audit({"event": "EvidenceCollected", "evidence_id": evidence_id, "type": evidence_type, "priority": priority})

    hash_display = f"`{file_hash[:32]}…`" if file_hash else "_file not accessible_"
    emit(hook_context(
        f"📦 **EVIDENCE COLLECTED — {priority} PRIORITY**\n\n"
        f"**ID:** `{evidence_id}`\n"
        f"**Type:** {evidence_type}\n"
        f"**Source:** `{evidence_path}`\n"
        f"**Method:** {collection_method}\n"
        f"**Collector:** {agent_name}\n\n"
        f"**Integrity (BLAKE2b-256):** {hash_display}\n"
        f"**Size:** {f'{file_size:,} bytes' if file_size else 'N/A'}\n\n"
        "**Chain of custody initialized.** Evidence preserved in investigation directory."
    ))


if __name__ == "__main__":
    asyncio.run(main())

