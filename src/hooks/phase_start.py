#!/usr/bin/env python3
"""
PhaseStart Hook — fires when a cybersecsuite investigation phase begins.
Creates phase directory structure, MITRE mapping, sets context.
"""
import asyncio
import json
import os
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import ensure_structure, get_session_dir, audit, append_file, emit, hook_context, read_stdin

PHASE_OBJECTIVES = {
    "Rapid Recon":        ["System profiling", "Process enumeration", "Network topology discovery", "Initial threat surface"],
    "Deep Scan":          ["Filesystem analysis", "Configuration audit", "Package integrity", "Service inspection"],
    "Network Analysis":   ["Traffic pattern analysis", "C2 detection", "DNS analysis", "Firewall rule review"],
    "Persistence Hunt":   ["Startup mechanisms", "Scheduled tasks", "Service persistence", "Cron analysis"],
    "Memory Forensics":   ["Process memory inspection", "Injection detection", "Rootkit detection", "Credential extraction"],
    "IOC Correlation":    ["Cross-referencing IOCs", "Timeline reconstruction", "Attack vector mapping", "Attribution"],
    "Threat Attribution": ["MITRE ATT&CK mapping", "APT correlation", "TTP identification", "Confidence scoring"],
    "Artifact Signing":   ["Sign collected artifacts", "Verify chain of custody", "BLAKE2b checksums", "Ed25519 signatures"],
}

PHASE_MITRE = {
    "Rapid Recon":        ["TA0007 - Discovery", "TA0043 - Reconnaissance"],
    "Deep Scan":          ["TA0003 - Persistence", "TA0005 - Defense Evasion", "TA0007 - Discovery"],
    "Network Analysis":   ["TA0001 - Initial Access", "TA0008 - Lateral Movement", "TA0011 - C2", "TA0010 - Exfiltration"],
    "Persistence Hunt":   ["TA0003 - Persistence", "TA0004 - Privilege Escalation"],
    "Memory Forensics":   ["TA0002 - Execution", "TA0005 - Defense Evasion", "TA0006 - Credential Access"],
    "IOC Correlation":    ["All tactics — comprehensive correlation"],
    "Threat Attribution": ["Cross-tactic campaign analysis"],
    "Artifact Signing":   ["Forensic chain-of-custody enforcement"],
}


async def main():
    ensure_structure()
    data = read_stdin()

    phase_name     = data.get("phase_name") or os.environ.get("CYBERSEC_PHASE", "Unknown Phase")
    investigation_id = data.get("investigation_id") or os.environ.get("CYBERSEC_INVESTIGATION_ID",
                        datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"))

    session_dir = get_session_dir()
    now         = datetime.now(timezone.utc)

    # Create phase directories
    if session_dir:
        phase_dir = session_dir / "phases" / phase_name.lower().replace(" ", "_")
        for sub in ["artifacts", "iocs", "evidence", "logs", "reports"]:
            (phase_dir / sub).mkdir(parents=True, exist_ok=True)

        # Phase metadata
        meta = {
            "phase_name":      phase_name,
            "investigation_id": investigation_id,
            "start_time":       now.isoformat(),
            "status":           "active",
            "objectives":       PHASE_OBJECTIVES.get(phase_name, ["Evidence collection", "IOC identification"]),
            "mitre_tactics":    PHASE_MITRE.get(phase_name, ["TA0007 - Discovery"]),
            "host":             socket.gethostname(),
        }
        (phase_dir / "phase_metadata.json").write_text(json.dumps(meta, indent=2))

        # Timeline
        timeline = session_dir / "timeline.md"
        append_file(timeline, f"| {now.strftime('%H:%M:%S')} | phase_start | **{phase_name}** | investigation={investigation_id} |\n")

    audit({"event": "PhaseStart", "phase": phase_name, "investigation_id": investigation_id})

    objs    = "\n".join(f"• {o}" for o in PHASE_OBJECTIVES.get(phase_name, ["Evidence collection"]))
    tactics = "\n".join(f"• {t}" for t in PHASE_MITRE.get(phase_name, ["TA0007"]))

    emit(hook_context(
        f"🔍 **PHASE STARTED: {phase_name.upper()}**\n"
        f"Investigation: `{investigation_id}` | {now.strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        f"**Objectives:**\n{objs}\n\n"
        f"**MITRE ATT&CK:**\n{tactics}\n\n"
        f"**Directories:** artifacts/ iocs/ evidence/ logs/ reports/\n\n"
        f"Ready for `{phase_name}` phase."
    ))


if __name__ == "__main__":
    asyncio.run(main())

