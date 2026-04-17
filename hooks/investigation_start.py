#!/usr/bin/env python3
"""
MalwareHunter Investigation Start Hook
Initializes comprehensive APT investigation with MalwareHunter framework setup
"""

import asyncio
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from utils import ensure_structure, get_session_dir, get_project_dir
from uvloop_integration import run_with_uvloop


async def investigation_start_async():
    """Initialize comprehensive APT investigation"""

    # Get investigation parameters
    investigation_id = os.environ.get('MALWARE_INVESTIGATION_ID',
                                    datetime.now().strftime('%Y%m%d_%H%M%S'))
    threat_scenario = os.environ.get('MALWARE_THREAT_SCENARIO',
                                   sys.argv[1] if len(sys.argv) > 1 else 'General APT Investigation')
    target_system = os.environ.get('MALWARE_TARGET_SYSTEM', 'auto-detected')

    # Ensure directory structure
    ensure_structure()
    session_dir = get_session_dir()
    project_dir = get_project_dir()

    # Create comprehensive investigation structure
    if session_dir:
        investigation_dir = session_dir / investigation_id
        investigation_dir.mkdir(parents=True, exist_ok=True)

        # Create MalwareHunter directory structure
        malware_hunter_dirs = [
            "artifacts/network",
            "artifacts/proc_net",
            "artifacts/processes",
            "artifacts/browser",
            "artifacts/firmware",
            "artifacts/kernel",
            "artifacts/ebpf",
            "artifacts/packages",
            "artifacts/logs",
            "artifacts/binaries",
            "artifacts/memory",
            "artifacts/screenshots",
            "artifacts/raw",
            "raw_dumps",
            "phases",
            "iocs",
            "reports",
            "timeline"
        ]

        for dir_path in malware_hunter_dirs:
            (investigation_dir / dir_path).mkdir(parents=True, exist_ok=True)

    # Initialize investigation metadata
    investigation_metadata = {
        "investigation_id": investigation_id,
        "threat_scenario": threat_scenario,
        "target_system": target_system,
        "start_time": datetime.now(datetime.UTC).isoformat(),
        "status": "active",
        "investigator": os.environ.get('USER', 'unknown'),
        "framework": "MalwareHunter",
        "version": "1.0",
        "system_profile": await detect_system_profile(),
        "threat_model": get_threat_model_for_scenario(threat_scenario),
        "investigation_phases": get_investigation_phases(),
        "attack_surface": await assess_attack_surface(),
        "detection_capabilities": get_detection_capabilities()
    }

    # Save investigation metadata
    if session_dir:
        metadata_file = investigation_dir / "investigation_metadata.json"
        metadata_file.write_text(json.dumps(investigation_metadata, indent=2))

        # Initialize investigation timeline
        await initialize_investigation_timeline(investigation_dir, investigation_metadata)

        # Create session manifest
        await create_session_manifest(investigation_dir, investigation_metadata)

        # Set environment variables for subsequent hooks
        os.environ['MALWARE_INVESTIGATION_DIR'] = str(investigation_dir)
        os.environ['MALWARE_INVESTIGATION_ID'] = investigation_id

    # Prepare investigation context
    investigation_context = await prepare_investigation_context(threat_scenario, investigation_metadata)

    # Generate output for Claude
    output = {
        "hookSpecificOutput": {
            "additionalContext": f"""🛡️ **MALWAREHUNTER INVESTIGATION INITIATED**

📋 **Investigation Setup:**
• Investigation ID: {investigation_id}
• Threat Scenario: {threat_scenario}
• Target System: {target_system}
• Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• Framework: MalwareHunter v1.0

🖥️ **System Profile:**
{format_system_profile(investigation_metadata['system_profile'])}

🎯 **Threat Model:**
{format_threat_model(investigation_metadata['threat_model'])}

📊 **Attack Surface Assessment:**
{format_attack_surface(investigation_metadata['attack_surface'])}

🔍 **Detection Capabilities:**
{format_detection_capabilities(investigation_metadata['detection_capabilities'])}

📁 **Investigation Structure:**
{format_investigation_structure(investigation_dir if session_dir else None)}

🚀 **Investigation Phases:**
{format_investigation_phases(investigation_metadata['investigation_phases'])}

{investigation_context}

**MalwareHunter investigation framework ready. Beginning with Phase 1 - Rapid Recon.**"""
        }
    }

    print(json.dumps(output))


async def detect_system_profile():
    """Auto-detect target system profile"""
    import platform
    import socket
    import subprocess

    try:
        hostname = socket.gethostname()
    except:
        hostname = "unknown"

    profile = {
        "hostname": hostname,
        "os": platform.system(),
        "os_version": platform.release(),
        "architecture": platform.machine(),
        "kernel": platform.release(),
        "filesystem": "auto-detected",
        "gpu": "auto-detected",
        "desktop": "auto-detected",
        "security_features": [],
        "hardware_security": "auto-assessed"
    }

    # Detect Linux distribution
    if profile["os"] == "Linux":
        try:
            result = subprocess.run(['lsb_release', '-d'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                profile["distribution"] = result.stdout.split('\t')[1].strip()
        except:
            try:
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('PRETTY_NAME='):
                            profile["distribution"] = line.split('=')[1].strip('"')
                            break
            except:
                profile["distribution"] = "Unknown Linux"

        # Check for security features
        security_features = []
        try:
            # Check for Secure Boot
            secureboot_path = Path('/sys/firmware/efi/efivars/SecureBoot-8be4df61-93ca-11d2-aa0d-00e098032b8c')
            if secureboot_path.exists():
                security_features.append("Secure Boot")
        except:
            pass

        try:
            # Check for IOMMU
            result = subprocess.run(['dmesg'], capture_output=True, text=True, timeout=5)
            if 'IOMMU' in result.stdout:
                security_features.append("IOMMU")
        except:
            pass

        profile["security_features"] = security_features

    return profile


def get_threat_model_for_scenario(threat_scenario):
    """Get threat model based on investigation scenario"""

    threat_models = {
        "Desktop screenshot exfiltration via C2 channels": {
            "attack_vectors": [
                "GPU/framebuffer access monitoring",
                "Screen capture malware",
                "C2 communication channels",
                "Data exfiltration"
            ],
            "detection_focus": [
                "/dev/fb* access",
                "GPU device monitoring",
                "Browser network activity",
                "Unusual display processes"
            ],
            "mitre_tactics": ["TA0009", "TA0011", "TA0010"],  # Collection, C2, Exfiltration
            "priority": "HIGH"
        },
        "Shell configuration tampering": {
            "attack_vectors": [
                "Shell config modification",
                "LD_PRELOAD injection",
                "Environment variable tampering",
                "Profile script modification"
            ],
            "detection_focus": [
                "Shell configs analysis",
                "Library injection detection",
                "Environment monitoring",
                "Profile integrity"
            ],
            "mitre_tactics": ["TA0003", "TA0005"],  # Persistence, Defense Evasion
            "priority": "MEDIUM"
        },
        "Browser session hijacking and cookie theft": {
            "attack_vectors": [
                "Browser session manipulation",
                "Cookie database theft",
                "Browser extension abuse",
                "DOM injection"
            ],
            "detection_focus": [
                "Browser forensics",
                "Cookie analysis",
                "Extension inspection",
                "Browser process monitoring"
            ],
            "mitre_tactics": ["TA0006", "TA0009"],  # Credential Access, Collection
            "priority": "HIGH"
        },
        "General APT Investigation": {
            "attack_vectors": [
                "Multi-stage attack campaign",
                "Persistence mechanisms",
                "Lateral movement",
                "Data exfiltration"
            ],
            "detection_focus": [
                "Comprehensive system analysis",
                "Network traffic monitoring",
                "Process behavior analysis",
                "File system integrity"
            ],
            "mitre_tactics": ["TA0001", "TA0002", "TA0003", "TA0006", "TA0008", "TA0010"],
            "priority": "HIGH"
        }
    }

    return threat_models.get(threat_scenario, threat_models["General APT Investigation"])


async def assess_attack_surface():
    """Assess system attack surface"""

    attack_surface = {
        "network_exposure": "auto-assessed",
        "running_services": "auto-enumerated",
        "open_ports": "auto-scanned",
        "installed_packages": "auto-inventoried",
        "user_accounts": "auto-enumerated",
        "privilege_levels": "auto-assessed",
        "security_controls": "auto-evaluated"
    }

    # Could be enhanced with actual system scanning
    return attack_surface


def get_detection_capabilities():
    """Define available detection capabilities"""

    return {
        "rootkit_detection": ["rkhunter", "unhide", "unhide-tcp"],
        "malware_scanning": ["lynis", "bpftool"],
        "firmware_analysis": ["fwupdmgr", "efibootmgr", "mokutil", "lsinitcpio"],
        "system_analysis": ["dmesg", "journalctl", "systemctl", "auditctl"],
        "process_analysis": ["lsof", "strace", "ltrace", "pmap"],
        "network_analysis": ["ss", "nmap", "tcpdump", "tshark"],
        "forensic_tools": ["binwalk", "yara", "snapper"],
        "privilege_tools": "sudo NOPASSWD configured"
    }


def get_investigation_phases():
    """Define MalwareHunter investigation phases"""

    return [
        {
            "phase": "Phase 1 - Rapid Recon",
            "description": "Initial system assessment and threat surface mapping",
            "objectives": [
                "System profiling",
                "Running process enumeration",
                "Network connection analysis",
                "Initial IOC discovery"
            ]
        },
        {
            "phase": "Phase 2 - Deep Scan",
            "description": "Comprehensive system analysis and rootkit detection",
            "objectives": [
                "Rootkit scanning",
                "File system analysis",
                "Package integrity verification",
                "Configuration tampering detection"
            ]
        },
        {
            "phase": "Phase 3 - Network Analysis",
            "description": "Network traffic analysis and C2 detection",
            "objectives": [
                "Traffic pattern analysis",
                "C2 communication detection",
                "DNS analysis",
                "Network IOC identification"
            ]
        },
        {
            "phase": "Phase 4 - Persistence Hunt",
            "description": "Persistence mechanism identification and analysis",
            "objectives": [
                "Startup mechanism analysis",
                "Service persistence detection",
                "Registry/config persistence",
                "Scheduled task analysis"
            ]
        },
        {
            "phase": "Phase 5 - Memory Forensics",
            "description": "Memory analysis and injection detection",
            "objectives": [
                "Process injection detection",
                "Memory artifact extraction",
                "Rootkit detection",
                "Credential analysis"
            ]
        },
        {
            "phase": "Phase 6 - Evidence Correlation",
            "description": "IOC correlation and timeline reconstruction",
            "objectives": [
                "IOC cross-referencing",
                "Attack timeline reconstruction",
                "Evidence correlation",
                "Impact assessment"
            ]
        }
    ]


async def initialize_investigation_timeline(investigation_dir, metadata):
    """Initialize investigation timeline"""

    timeline_entry = {
        "timestamp": datetime.now(datetime.UTC).isoformat(),
        "event_type": "investigation_start",
        "investigation_id": metadata["investigation_id"],
        "threat_scenario": metadata["threat_scenario"],
        "system_profile": metadata["system_profile"],
        "metadata": metadata
    }

    timeline_file = investigation_dir / "timeline.md"
    timeline_json = investigation_dir / "timeline" / "investigation_timeline.json"

    # Create JSON timeline
    timeline_json.parent.mkdir(exist_ok=True)
    timeline_json.write_text(json.dumps([timeline_entry], indent=2))

    # Create markdown timeline
    markdown_content = f"""# Investigation Timeline

## {metadata['investigation_id']} - {metadata['threat_scenario']}

### Investigation Start
- **Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Investigator**: {metadata['investigator']}
- **Target System**: {metadata['target_system']}
- **Framework**: MalwareHunter v1.0

### System Profile
- **OS**: {metadata['system_profile']['os']} {metadata['system_profile']['os_version']}
- **Hostname**: {metadata['system_profile']['hostname']}
- **Architecture**: {metadata['system_profile']['architecture']}

---
*Timeline will be updated as investigation progresses*
"""

    timeline_file.write_text(markdown_content)


async def create_session_manifest(investigation_dir, metadata):
    """Create session manifest file"""

    manifest = {
        "investigation": metadata,
        "directory_structure": {
            "artifacts": "Evidence collection directory",
            "raw_dumps": "Raw data dumps",
            "phases": "Phase-specific analysis",
            "iocs": "Indicators of Compromise",
            "reports": "Investigation reports",
            "timeline": "Investigation timeline"
        },
        "rules": [
            "Always non-destructive first (read-only)",
            "Never delete, modify or kill without explicit confirmation",
            "Cross-validate every finding with at least two independent sources",
            "Assume advanced evasion techniques",
            "Document every finding with severity, evidence, IOCs and next action"
        ],
        "created": datetime.now(datetime.UTC).isoformat()
    }

    manifest_file = investigation_dir / "manifest.json"
    manifest_file.write_text(json.dumps(manifest, indent=2))


async def prepare_investigation_context(threat_scenario, metadata):
    """Prepare scenario-specific investigation context"""

    context_templates = {
        "Desktop screenshot exfiltration via C2 channels": """
🖥️ **DESKTOP SCREENSHOT EXFILTRATION INVESTIGATION**

**Priority Investigation Areas:**
1. GPU/Framebuffer Access Monitoring
2. Screen Capture Process Detection
3. C2 Communication Analysis
4. Browser Network Activity

**Key Commands to Execute:**
• `sudo lsof /dev/fb*` - Check framebuffer access
• `ps aux | grep -E "(screenshot|capture|screen)"` - Screen processes
• `sudo ss -tuln | grep -E "(443|80|8080)"` - Suspicious connections
• `ls -la ~/.config/autostart/` - Check autostart persistence

**IOCs to Investigate:**
• Processes with GPU device access
• Unusual network connections from desktop processes
• Screen capture binaries in temporary directories
• Suspicious browser extensions or plugins""",

        "Shell configuration tampering": """
🐚 **SHELL CONFIGURATION TAMPERING INVESTIGATION**

**Priority Investigation Areas:**
1. Shell Configuration Analysis
2. LD_PRELOAD Detection
3. Environment Variable Tampering
4. Profile Script Integrity

**Key Commands to Execute:**
• `find /home -name ".*rc" -o -name ".*profile" -mtime -7` - Recent config changes
• `env | grep -i preload` - Check LD_PRELOAD
• `sudo find /etc -name "profile*" -o -name "bashrc*" -mtime -7` - System configs
• `ldd /bin/bash` - Check bash library dependencies

**IOCs to Investigate:**
• Modified shell configuration files
• Suspicious LD_PRELOAD entries
• Unknown libraries in shell environment
• Unusual aliases or functions in profiles""",

        "Browser session hijacking and cookie theft": """
🌐 **BROWSER SESSION HIJACKING INVESTIGATION**

**Priority Investigation Areas:**
1. Browser Process Analysis
2. Cookie Database Examination
3. Extension Security Analysis
4. Session Token Monitoring

**Key Commands to Execute:**
• `ps aux | grep -E "(firefox|chrome|chromium)"` - Browser processes
• `find ~/.mozilla ~/.config/google-chrome -name "cookies*"` - Cookie databases
• `ls -la ~/.mozilla/firefox/*/extensions/` - Firefox extensions
• `netstat -an | grep :443` - HTTPS connections

**IOCs to Investigate:**
• Suspicious browser extensions
• Modified cookie databases
• Unusual browser network connections
• Session hijacking scripts or tools"""
    }

    return context_templates.get(threat_scenario, """
🔍 **GENERAL APT INVESTIGATION**

**Comprehensive Analysis Approach:**
1. System profiling and baseline establishment
2. Multi-phase investigation workflow
3. IOC discovery and correlation
4. Threat attribution and impact assessment

**Investigation will proceed through all MalwareHunter phases systematically.**""")


def format_system_profile(profile):
    """Format system profile for display"""
    os_info = f"{profile.get('os', 'Unknown')} {profile.get('os_version', '')}"
    if 'distribution' in profile:
        os_info = profile['distribution']

    security = ", ".join(profile.get('security_features', [])) or "None detected"

    return f"""• OS: {os_info}
• Hostname: {profile.get('hostname', 'unknown')}
• Architecture: {profile.get('architecture', 'unknown')}
• Security Features: {security}"""


def format_threat_model(threat_model):
    """Format threat model for display"""
    vectors = "\n".join(f"  • {vector}" for vector in threat_model.get('attack_vectors', []))
    focus = "\n".join(f"  • {item}" for item in threat_model.get('detection_focus', []))

    return f"""Attack Vectors:
{vectors}
Detection Focus:
{focus}
Priority: {threat_model.get('priority', 'MEDIUM')}"""


def format_attack_surface(attack_surface):
    """Format attack surface for display"""
    items = []
    for key, value in attack_surface.items():
        formatted_key = key.replace('_', ' ').title()
        items.append(f"• {formatted_key}: {value}")

    return "\n".join(items)


def format_detection_capabilities(capabilities):
    """Format detection capabilities for display"""
    formatted = []
    for category, tools in capabilities.items():
        if isinstance(tools, list):
            tool_list = ", ".join(tools)
            formatted.append(f"• {category.replace('_', ' ').title()}: {tool_list}")
        else:
            formatted.append(f"• {category.replace('_', ' ').title()}: {tools}")

    return "\n".join(formatted)


def format_investigation_structure(investigation_dir):
    """Format investigation structure for display"""
    if not investigation_dir or not investigation_dir.exists():
        return "• Investigation structure will be created in session context"

    return f"""• Investigation Directory: {investigation_dir.name}
• Artifacts: Network, Processes, Browser, Firmware, Kernel, eBPF
• Raw Dumps: Binary evidence preservation
• Phases: Phase-specific analysis results
• IOCs: Indicators of Compromise documentation
• Reports: Investigation findings and analysis
• Timeline: Chronological investigation log"""


def format_investigation_phases(phases):
    """Format investigation phases for display"""
    formatted = []
    for i, phase in enumerate(phases, 1):
        formatted.append(f"{i}. {phase['phase']}")
        formatted.append(f"   {phase['description']}")

    return "\n".join(formatted)


def main():
    """Entry point with uvloop optimization"""
    run_with_uvloop(investigation_start_async())


if __name__ == "__main__":
    main()