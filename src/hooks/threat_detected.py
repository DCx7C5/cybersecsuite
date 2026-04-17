#!/usr/bin/env python3
"""
MalwareHunter Threat Detected Hook
Triggered when a potential threat is identified during investigation
"""

import json
import os
import sys
from datetime import datetime
from _utils import ensure_structure, get_session_dir
from uvloop_integration import run_with_uvloop


async def threat_detected_async():
    """Handle threat detection event"""

    # Get threat information from environment or arguments
    threat_type = os.environ.get('MALWARE_THREAT_TYPE', sys.argv[1] if len(sys.argv) > 1 else 'Unknown Threat')
    threat_severity = os.environ.get('MALWARE_THREAT_SEVERITY', 'medium')
    threat_source = os.environ.get('MALWARE_THREAT_SOURCE', 'investigation')
    investigation_id = os.environ.get('MALWARE_INVESTIGATION_ID', datetime.now().strftime('%Y%m%d_%H%M%S'))

    # Ensure directory structure
    ensure_structure()
    session_dir = get_session_dir()

    # Create threat record
    threat_record = {
        "threat_id": f"THREAT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "threat_type": threat_type,
        "severity": threat_severity,
        "source": threat_source,
        "investigation_id": investigation_id,
        "detection_time": datetime.now(datetime.UTC).isoformat(),
        "status": "detected",
        "investigator": os.environ.get('USER', 'unknown'),
        "threat_details": get_threat_details(threat_type),
        "response_recommendations": get_response_recommendations(threat_type, threat_severity),
        "mitre_mapping": get_mitre_mapping_for_threat(threat_type)
    }

    # Save threat record
    if session_dir:
        investigation_dir = session_dir / investigation_id
        threats_dir = investigation_dir / "threats"
        threats_dir.mkdir(parents=True, exist_ok=True)

        threat_file = threats_dir / f"threat_{threat_record['threat_id']}.json"
        threat_file.write_text(json.dumps(threat_record, indent=2))

        # Update investigation timeline
        await update_threat_timeline(investigation_dir, threat_record)

        # Create threat alert
        await create_threat_alert(investigation_dir, threat_record)

    # Determine urgency level
    urgency = determine_threat_urgency(threat_severity, threat_type)

    # Generate output for Claude
    output = {
        "hookSpecificOutput": {
            "additionalContext": f"""🚨 **THREAT DETECTED - {urgency.upper()} PRIORITY**

🎯 **Threat Information:**
• Threat ID: {threat_record['threat_id']}
• Type: {threat_type}
• Severity: {threat_severity.upper()}
• Source: {threat_source}
• Detection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚠️ **Threat Details:**
{format_threat_details(threat_record['threat_details'])}

🏛️ **MITRE ATT&CK Mapping:**
{format_mitre_mapping(threat_record['mitre_mapping'])}

🛡️ **Immediate Response Recommendations:**
{format_response_recommendations(threat_record['response_recommendations'])}

📋 **Investigation Actions:**
{format_investigation_actions(threat_type, threat_severity)}

🔄 **Next Steps:**
{format_next_steps(threat_type, threat_severity)}

**Threat detection logged and investigation protocols activated.**"""
        }
    }

    print(json.dumps(output))


def get_threat_details(threat_type):
    """Get detailed information about the threat type"""

    threat_details = {
        "Rootkit Detection": {
            "description": "Potential rootkit or kernel-level malware detected",
            "indicators": [
                "Hidden processes or files",
                "Kernel module tampering",
                "System call hooking",
                "Memory injection patterns"
            ],
            "impact": "System-level compromise, potential data theft",
            "persistence": "Kernel-level persistence mechanisms"
        },
        "C2 Communication": {
            "description": "Command and Control communication detected",
            "indicators": [
                "Suspicious network connections",
                "Encrypted communication channels",
                "Domain generation algorithms",
                "Beaconing patterns"
            ],
            "impact": "Remote attacker control, data exfiltration",
            "persistence": "Network-based command channels"
        },
        "Process Injection": {
            "description": "Code injection into legitimate processes detected",
            "indicators": [
                "DLL injection patterns",
                "Process hollowing",
                "Reflective DLL loading",
                "Memory manipulation"
            ],
            "impact": "Stealth execution, privilege escalation",
            "persistence": "Process-based hiding techniques"
        },
        "Browser Hijacking": {
            "description": "Browser session manipulation detected",
            "indicators": [
                "Cookie theft",
                "Session token manipulation",
                "Extension tampering",
                "DOM modification"
            ],
            "impact": "Session hijacking, credential theft",
            "persistence": "Browser-based persistence"
        },
        "Kerberos Attack": {
            "description": "Kerberos authentication attack detected",
            "indicators": [
                "Ticket extraction",
                "Credential dumping",
                "Golden/Silver tickets",
                "SPN enumeration"
            ],
            "impact": "Domain compromise, lateral movement",
            "persistence": "AD-based persistence mechanisms"
        },
        "Data Exfiltration": {
            "description": "Unauthorized data transfer detected",
            "indicators": [
                "Large data transfers",
                "Encrypted archives",
                "Covert channels",
                "Cloud uploads"
            ],
            "impact": "Data theft, intellectual property loss",
            "persistence": "Data collection mechanisms"
        }
    }

    return threat_details.get(threat_type, {
        "description": f"Unknown threat type: {threat_type}",
        "indicators": ["Requires further analysis"],
        "impact": "Impact assessment pending",
        "persistence": "Persistence mechanisms unknown"
    })


def get_response_recommendations(threat_type, severity):
    """Get response recommendations based on threat type and severity"""

    base_recommendations = {
        "critical": [
            "Immediately isolate affected systems",
            "Activate incident response team",
            "Preserve forensic evidence",
            "Notify security operations center"
        ],
        "high": [
            "Contain threat spread",
            "Implement monitoring controls",
            "Collect additional evidence",
            "Prepare containment measures"
        ],
        "medium": [
            "Continue detailed investigation",
            "Monitor for escalation",
            "Document findings thoroughly",
            "Implement preventive controls"
        ],
        "low": [
            "Continue monitoring",
            "Document for future reference",
            "Update threat intelligence",
            "Review detection rules"
        ]
    }

    threat_specific = {
        "Rootkit Detection": [
            "Boot from clean external media",
            "Perform offline analysis",
            "Check kernel integrity",
            "Scan with multiple anti-rootkit tools"
        ],
        "C2 Communication": [
            "Block identified C2 domains/IPs",
            "Capture network traffic",
            "Analyze communication protocols",
            "Implement DNS monitoring"
        ],
        "Process Injection": [
            "Analyze process memory",
            "Identify injection techniques",
            "Scan for malicious DLLs",
            "Monitor process creation"
        ],
        "Browser Hijacking": [
            "Reset browser profiles",
            "Analyze cookie databases",
            "Check browser extensions",
            "Monitor web traffic"
        ],
        "Kerberos Attack": [
            "Reset KRBTGT password",
            "Monitor Kerberos events",
            "Check for golden tickets",
            "Analyze service accounts"
        ],
        "Data Exfiltration": [
            "Block external transfers",
            "Analyze data pathways",
            "Check for encrypted archives",
            "Monitor cloud uploads"
        ]
    }

    recommendations = base_recommendations.get(severity.lower(), base_recommendations["medium"])
    specific_recs = threat_specific.get(threat_type, [])

    return {
        "immediate": recommendations,
        "threat_specific": specific_recs,
        "timeline": get_response_timeline(severity)
    }


def get_mitre_mapping_for_threat(threat_type):
    """Map threat type to MITRE ATT&CK techniques"""

    mitre_mappings = {
        "Rootkit Detection": {
            "tactics": ["TA0005"],  # Defense Evasion
            "techniques": ["T1014", "T1055", "T1027"],  # Rootkit, Process Injection, Obfuscation
            "description": "Advanced evasion and stealth techniques"
        },
        "C2 Communication": {
            "tactics": ["TA0011"],  # Command and Control
            "techniques": ["T1071", "T1573", "T1008"],  # Application Layer, Encrypted Channel, Fallback
            "description": "Command and control infrastructure"
        },
        "Process Injection": {
            "tactics": ["TA0005", "TA0004"],  # Defense Evasion, Privilege Escalation
            "techniques": ["T1055"],  # Process Injection
            "sub_techniques": ["T1055.001", "T1055.002", "T1055.003"],
            "description": "Code injection and process manipulation"
        },
        "Browser Hijacking": {
            "tactics": ["TA0006", "TA0009"],  # Credential Access, Collection
            "techniques": ["T1539", "T1185"],  # Steal Web Session Cookie, Browser Session Hijacking
            "description": "Web browser compromise and data theft"
        },
        "Kerberos Attack": {
            "tactics": ["TA0006"],  # Credential Access
            "techniques": ["T1558"],  # Steal or Forge Kerberos Tickets
            "sub_techniques": ["T1558.001", "T1558.003"],  # Golden Ticket, Kerberoasting
            "description": "Kerberos authentication attacks"
        },
        "Data Exfiltration": {
            "tactics": ["TA0010"],  # Exfiltration
            "techniques": ["T1041", "T1567", "T1022"],  # C2 Channel, Cloud Storage, Data Encrypted
            "description": "Unauthorized data transfer"
        }
    }

    return mitre_mappings.get(threat_type, {
        "tactics": ["TA0007"],  # Discovery
        "techniques": ["T1082"],  # System Information Discovery
        "description": "Threat analysis pending"
    })


def determine_threat_urgency(severity, threat_type):
    """Determine urgency level for threat response"""

    urgency_matrix = {
        "critical": "IMMEDIATE",
        "high": "URGENT",
        "medium": "ELEVATED",
        "low": "ROUTINE"
    }

    base_urgency = urgency_matrix.get(severity.lower(), "ELEVATED")

    # Escalate for certain threat types
    high_priority_threats = ["Rootkit Detection", "C2 Communication", "Data Exfiltration"]
    if threat_type in high_priority_threats and severity.lower() in ["medium", "high"]:
        if base_urgency == "ELEVATED":
            base_urgency = "URGENT"
        elif base_urgency == "URGENT":
            base_urgency = "IMMEDIATE"

    return base_urgency


def get_response_timeline(severity):
    """Get response timeline based on severity"""

    timelines = {
        "critical": "Immediate (0-15 minutes)",
        "high": "Urgent (15-60 minutes)",
        "medium": "Elevated (1-4 hours)",
        "low": "Routine (4-24 hours)"
    }

    return timelines.get(severity.lower(), "4-24 hours")


async def update_threat_timeline(investigation_dir, threat_record):
    """Update investigation timeline with threat detection"""

    timeline_file = investigation_dir / "timeline" / "investigation_timeline.json"
    timeline_file.parent.mkdir(exist_ok=True)

    timeline_entry = {
        "timestamp": datetime.now(datetime.UTC).isoformat(),
        "event_type": "threat_detected",
        "threat_id": threat_record["threat_id"],
        "threat_type": threat_record["threat_type"],
        "severity": threat_record["severity"],
        "metadata": threat_record
    }

    # Load existing timeline or create new
    timeline = []
    if timeline_file.exists():
        try:
            timeline = json.loads(timeline_file.read_text())
        except (json.JSONDecodeError, OSError):
            timeline = []

    timeline.append(timeline_entry)
    timeline_file.write_text(json.dumps(timeline, indent=2))


async def create_threat_alert(investigation_dir, threat_record):
    """Create threat alert for immediate attention"""

    alerts_dir = investigation_dir / "alerts"
    alerts_dir.mkdir(exist_ok=True)

    alert = {
        "alert_id": f"ALERT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "threat_id": threat_record["threat_id"],
        "alert_level": determine_threat_urgency(threat_record["severity"], threat_record["threat_type"]),
        "created": datetime.now(datetime.UTC).isoformat(),
        "status": "active",
        "summary": f"{threat_record['threat_type']} detected with {threat_record['severity']} severity",
        "response_required": True,
        "escalation_needed": threat_record["severity"].lower() in ["critical", "high"]
    }

    alert_file = alerts_dir / f"alert_{alert['alert_id']}.json"
    alert_file.write_text(json.dumps(alert, indent=2))


def format_threat_details(details):
    """Format threat details for display"""
    if not details:
        return "• Threat details pending analysis"

    formatted = [
        f"• Description: {details.get('description', 'Unknown')}",
        f"• Impact: {details.get('impact', 'Unknown')}",
        f"• Persistence: {details.get('persistence', 'Unknown')}"
    ]

    indicators = details.get('indicators', [])
    if indicators:
        formatted.append("• Key Indicators:")
        for indicator in indicators[:3]:  # Show top 3
            formatted.append(f"  - {indicator}")

    return "\n".join(formatted)


def format_mitre_mapping(mapping):
    """Format MITRE mapping for display"""
    if not mapping:
        return "• MITRE mapping pending"

    tactics = ", ".join(mapping.get('tactics', []))
    techniques = ", ".join(mapping.get('techniques', []))

    return f"""• Tactics: {tactics}
• Techniques: {techniques}
• Description: {mapping.get('description', 'Unknown')}"""


def format_response_recommendations(recommendations):
    """Format response recommendations for display"""
    if not recommendations:
        return "• Response recommendations pending"

    immediate = recommendations.get('immediate', [])
    specific = recommendations.get('threat_specific', [])
    timeline = recommendations.get('timeline', 'Unknown')

    formatted = [f"Timeline: {timeline}"]

    if immediate:
        formatted.append("Immediate Actions:")
        for action in immediate[:3]:  # Show top 3
            formatted.append(f"  • {action}")

    if specific:
        formatted.append("Threat-Specific Actions:")
        for action in specific[:2]:  # Show top 2
            formatted.append(f"  • {action}")

    return "\n".join(formatted)


def format_investigation_actions(threat_type, severity):
    """Format investigation actions for threat"""

    actions = [
        "Preserve current system state for analysis",
        "Collect additional forensic evidence",
        "Document all threat indicators",
        "Cross-reference with known threat intelligence"
    ]

    if severity.lower() in ["critical", "high"]:
        actions.extend([
            "Activate incident response procedures",
            "Notify security stakeholders",
            "Prepare containment measures"
        ])

    return "\n".join(f"• {action}" for action in actions[:5])


def format_next_steps(threat_type, severity):
    """Format next steps based on threat"""

    if severity.lower() == "critical":
        steps = [
            "Execute immediate containment",
            "Escalate to incident response team",
            "Begin damage assessment"
        ]
    elif severity.lower() == "high":
        steps = [
            "Continue investigation with elevated priority",
            "Implement additional monitoring",
            "Prepare response measures"
        ]
    else:
        steps = [
            "Continue systematic investigation",
            "Monitor for threat escalation",
            "Update threat intelligence"
        ]

    return "\n".join(f"• {step}" for step in steps)


def main():
    """Entry point with uvloop optimization"""
    run_with_uvloop(threat_detected_async())


if __name__ == "__main__":
    main()