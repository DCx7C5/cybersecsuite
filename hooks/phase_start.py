#!/usr/bin/env python3
"""
MalwareHunter Phase Start Hook
Initializes investigation phase with structured logging and IOC tracking
"""

import json
import os
import sys
from datetime import UTC, datetime
from utils import ensure_structure, get_session_dir, get_project_dir
from uvloop_integration import run_with_uvloop


async def phase_start_async():
    """Handle investigation phase start with comprehensive setup"""

    # Get phase information from environment or arguments
    global phase_dir
    phase_name = os.environ.get('MALWARE_PHASE_NAME', sys.argv[1] if len(sys.argv) > 1 else 'Unknown Phase')
    investigation_id = os.environ.get('MALWARE_INVESTIGATION_ID', datetime.now().strftime('%Y%m%d_%H%M%S'))
    threat_scenario = os.environ.get('MALWARE_THREAT_SCENARIO', 'General APT Investigation')

    # Ensure directory structure
    ensure_structure()
    session_dir = get_session_dir()
    project_dir = get_project_dir()

    # Create phase-specific directories
    if session_dir:
        phase_dir = session_dir / "phases" / phase_name.lower().replace(' ', '_')
        phase_dir.mkdir(parents=True, exist_ok=True)

        # Create phase subdirectories
        (phase_dir / "artifacts").mkdir(exist_ok=True)
        (phase_dir / "iocs").mkdir(exist_ok=True)
        (phase_dir / "evidence").mkdir(exist_ok=True)
        (phase_dir / "logs").mkdir(exist_ok=True)
        (phase_dir / "reports").mkdir(exist_ok=True)

    # Initialize phase metadata
    phase_metadata = {
        "phase_name": phase_name,
        "investigation_id": investigation_id,
        "threat_scenario": threat_scenario,
        "start_time": datetime.now(datetime.UTC).isoformat(),
        "status": "active",
        "investigator": os.environ.get('USER', 'unknown'),
        "system_info": await get_system_info(),
        "phase_objectives": get_phase_objectives(phase_name),
        "expected_artifacts": get_expected_artifacts(phase_name),
        "mitre_tactics": get_mitre_tactics_for_phase(phase_name)
    }

    # Save phase metadata
    if session_dir:
        phase_metadata_file = phase_dir / "phase_metadata.json"
        phase_metadata_file.write_text(json.dumps(phase_metadata, indent=2))

        # Update investigation timeline
        await update_investigation_timeline(session_dir, phase_name, "start", phase_metadata)

    # Prepare phase-specific context
    phase_context = await prepare_phase_context(phase_name, phase_metadata)

    # Generate output for Claude
    output = {
        "hookSpecificOutput": {
            "additionalContext": f"""🔍 **MALWARE HUNTER PHASE STARTED: {phase_name.upper()}**

📋 **Investigation Context:**
• Investigation ID: {investigation_id}
• Threat Scenario: {threat_scenario}
• Phase Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• System: {phase_metadata['system_info']['hostname']} ({phase_metadata['system_info']['os']})

🎯 **Phase Objectives:**
{format_objectives(phase_metadata['phase_objectives'])}

🔧 **Expected Artifacts:**
{format_artifacts(phase_metadata['expected_artifacts'])}

🏛️ **MITRE ATT&CK Focus:**
{format_mitre_tactics(phase_metadata['mitre_tactics'])}

📂 **Phase Directory Structure Created:**
{format_directory_structure(phase_dir if session_dir else None)}

{phase_context}

**Ready to begin {phase_name} investigation phase.**"""
        }
    }

    print(json.dumps(output))


async def get_system_info():
    """Gather system information for investigation context"""
    import platform
    import socket

    try:
        hostname = socket.gethostname()
    except:
        hostname = "unknown"

    return {
        "hostname": hostname,
        "os": platform.system(),
        "os_version": platform.release(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "timestamp": datetime.now(datetime.UTC).isoformat()
    }


def get_phase_objectives(phase_name):
    """Get objectives specific to investigation phase"""
    phase_objectives = {
        "Rapid Recon": [
            "System profiling and baseline establishment",
            "Initial threat surface assessment",
            "Network topology discovery",
            "Running process enumeration",
            "Active connection monitoring"
        ],
        "Deep Scan": [
            "Comprehensive filesystem analysis",
            "Registry examination (Windows)",
            "Configuration file analysis",
            "Installed package verification",
            "Service and daemon inspection"
        ],
        "Network Analysis": [
            "Traffic pattern analysis",
            "C2 communication detection",
            "DNS query analysis",
            "Network share enumeration",
            "Firewall rule examination"
        ],
        "Persistence Hunt": [
            "Startup mechanism analysis",
            "Scheduled task inspection",
            "Service persistence detection",
            "Registry run key examination",
            "Cron job analysis"
        ],
        "Memory Forensics": [
            "Process memory inspection",
            "Heap/stack analysis",
            "Injected code detection",
            "Credential extraction",
            "Rootkit detection"
        ],
        "Evidence Correlation": [
            "IOC cross-referencing",
            "Timeline reconstruction",
            "Attack vector identification",
            "Attribution analysis",
            "Impact assessment"
        ],
        "Threat Attribution": [
            "MITRE ATT&CK mapping",
            "APT group correlation",
            "Campaign pattern analysis",
            "TTPs identification",
            "Confidence scoring"
        ]
    }

    return phase_objectives.get(phase_name, [
        "Phase-specific investigation objectives",
        "Evidence collection and analysis",
        "IOC identification and cataloging",
        "Threat assessment and documentation"
    ])


def get_expected_artifacts(phase_name):
    """Get expected artifacts for investigation phase"""
    phase_artifacts = {
        "Rapid Recon": [
            "System profile (OS, hardware, network)",
            "Process list with command lines",
            "Network connections and listening ports",
            "User account enumeration",
            "Initial suspicious indicators"
        ],
        "Deep Scan": [
            "File system timeline",
            "Configuration file dumps",
            "Package/software inventory",
            "Registry exports (Windows)",
            "Log file collections"
        ],
        "Network Analysis": [
            "Network traffic captures",
            "DNS query logs",
            "Firewall rule exports",
            "Network share discoveries",
            "C2 communication indicators"
        ],
        "Persistence Hunt": [
            "Startup item inventory",
            "Scheduled task exports",
            "Service configuration dumps",
            "Auto-run registry keys",
            "Boot process analysis"
        ],
        "Memory Forensics": [
            "Memory dump files",
            "Process injection evidence",
            "Extracted credentials",
            "Suspicious code segments",
            "Rootkit indicators"
        ],
        "Evidence Correlation": [
            "IOC correlation matrix",
            "Attack timeline",
            "Evidence chain documentation",
            "Attribution assessment",
            "Impact analysis report"
        ]
    }

    return phase_artifacts.get(phase_name, [
        "Digital evidence files",
        "Analysis reports",
        "IOC documentation",
        "Investigation logs"
    ])


def get_mitre_tactics_for_phase(phase_name):
    """Map investigation phases to relevant MITRE ATT&CK tactics"""
    phase_tactics = {
        "Rapid Recon": [
            "TA0007 - Discovery",
            "TA0043 - Reconnaissance"
        ],
        "Deep Scan": [
            "TA0003 - Persistence",
            "TA0005 - Defense Evasion",
            "TA0007 - Discovery"
        ],
        "Network Analysis": [
            "TA0001 - Initial Access",
            "TA0008 - Lateral Movement",
            "TA0011 - Command and Control",
            "TA0010 - Exfiltration"
        ],
        "Persistence Hunt": [
            "TA0003 - Persistence",
            "TA0004 - Privilege Escalation"
        ],
        "Memory Forensics": [
            "TA0002 - Execution",
            "TA0005 - Defense Evasion",
            "TA0006 - Credential Access"
        ],
        "Evidence Correlation": [
            "All tactics - comprehensive analysis"
        ],
        "Threat Attribution": [
            "Cross-tactic analysis for campaign attribution"
        ]
    }

    return phase_tactics.get(phase_name, ["TA0007 - Discovery"])


async def update_investigation_timeline(session_dir, phase_name, event_type, metadata):
    """Update investigation timeline with phase events"""
    timeline_file = session_dir / "investigation_timeline.json"

    timeline_entry = {
        "timestamp": datetime.now(datetime.UTC).isoformat(),
        "event_type": f"phase_{event_type}",
        "phase_name": phase_name,
        "investigation_id": metadata.get("investigation_id"),
        "metadata": metadata
    }

    # Load existing timeline or create new
    timeline = []
    if timeline_file.exists():
        try:
            timeline = json.loads(timeline_file.read_text())
        except:
            timeline = []

    timeline.append(timeline_entry)

    # Save updated timeline
    timeline_file.write_text(json.dumps(timeline, indent=2))


async def prepare_phase_context(phase_name, phase_metadata):
    """Prepare phase-specific context and guidance"""

    context_templates = {
        "Rapid Recon": """
🚀 **RAPID RECONNAISSANCE PHASE**

**Priority Actions:**
1. Execute `sudo dmesg | tail -50` - Check kernel messages
2. Run `ps aux --sort=-%cpu | head -20` - Identify CPU-intensive processes
3. Execute `ss -tuln` - Map network listeners
4. Run `sudo lsof -i` - Active network connections
5. Check `sudo systemctl list-units --failed` - Failed services

**Key Commands Ready:**
• Process analysis: `ps`, `pstree`, `lsof`
• Network analysis: `ss`, `netstat`, `tcpdump`
• System analysis: `uname`, `lscpu`, `lsmem`
• Security analysis: `sudo auditctl -l`, `journalctl`""",

        "Deep Scan": """
🔍 **DEEP SYSTEM SCAN PHASE**

**Priority Actions:**
1. Execute `sudo find /tmp /var/tmp -type f -mtime -1` - Recent temp files
2. Run `sudo rkhunter --check --skip-keypress` - Rootkit scan
3. Execute `sudo lynis audit system` - Security audit
4. Check `sudo find /etc -name "*.conf" -mtime -7` - Recent config changes
5. Run `sudo find / -perm -4000 -type f 2>/dev/null` - SUID binaries

**Analysis Focus:**
• Configuration tampering detection
• Unusual file modifications
• Package integrity verification
• Hidden file discovery""",

        "Network Analysis": """
🌐 **NETWORK ANALYSIS PHASE**

**Priority Actions:**
1. Execute `sudo tcpdump -i any -w network_capture.pcap &` - Start capture
2. Run `sudo arp -a` - ARP table analysis
3. Execute `sudo route -n` - Routing table examination
4. Check `sudo iptables -L -n -v` - Firewall rules
5. Run `sudo ss -plant` - Detailed connection info

**Focus Areas:**
• C2 communication patterns
• Lateral movement indicators
• DNS exfiltration detection
• Network persistence mechanisms""",

        "Memory Forensics": """
🧠 **MEMORY FORENSICS PHASE**

**Priority Actions:**
1. Execute `sudo strings /proc/kcore | grep -i "http\\|ftp\\|ssh"` - Memory strings
2. Run `sudo lsof +L1` - Deleted but open files
3. Execute `sudo pmap $suspicious_pid` - Process memory map
4. Check `sudo gcore $suspicious_pid` - Core dump suspicious process
5. Run `sudo volatility -f memory.dump imageinfo` - Memory analysis

**Analysis Targets:**
• Process injection evidence
• Credential extraction
• Code injection patterns
• Rootkit detection"""
    }

    return context_templates.get(phase_name, f"""
🔧 **{phase_name.upper()} PHASE**

**Investigation Focus:**
• Evidence collection and preservation
• IOC identification and documentation
• Threat analysis and correlation
• Artifact preservation and chain of custody

**Standard Procedure:**
1. Document all findings with timestamps
2. Preserve evidence integrity
3. Maintain detailed investigation logs
4. Cross-reference discovered IOCs""")


def format_objectives(objectives):
    """Format objectives for display"""
    return "\n".join(f"• {obj}" for obj in objectives)


def format_artifacts(artifacts):
    """Format artifacts for display"""
    return "\n".join(f"• {artifact}" for artifact in artifacts)


def format_mitre_tactics(tactics):
    """Format MITRE tactics for display"""
    return "\n".join(f"• {tactic}" for tactic in tactics)


def format_directory_structure(phase_dir: object) -> str:
    """Format directory structure for display"""
    if not phase_dir or not phase_dir.exists():
        return "• Phase directories will be created in session context"

    structure = [
        f"• {phase_dir}/artifacts/ - Evidence collection",
        f"• {phase_dir}/iocs/ - IOC documentation",
        f"• {phase_dir}/evidence/ - Digital evidence",
        f"• {phase_dir}/logs/ - Investigation logs",
        f"• {phase_dir}/reports/ - Analysis reports"
    ]

    return "\n".join(structure)


def main():
    """Entry point with uvloop optimization"""
    run_with_uvloop(phase_start_async())


if __name__ == "__main__":
    main()