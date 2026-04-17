#!/usr/bin/env python3
"""
MalwareHunter IOC Discovered Hook
Triggered when a new Indicator of Compromise is identified
"""

import asyncio
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from utils import ensure_structure, get_session_dir
from uvloop_integration import run_with_uvloop


async def ioc_discovered_async():
    """Handle IOC discovery event"""

    # Get IOC information from environment or arguments
    ioc_value = os.environ.get('MALWARE_IOC_VALUE', sys.argv[1] if len(sys.argv) > 1 else 'unknown')
    ioc_type = os.environ.get('MALWARE_IOC_TYPE', sys.argv[2] if len(sys.argv) > 2 else 'unknown')
    ioc_source = os.environ.get('MALWARE_IOC_SOURCE', 'investigation')
    investigation_id = os.environ.get('MALWARE_INVESTIGATION_ID', datetime.now().strftime('%Y%m%d_%H%M%S'))

    # Ensure directory structure
    ensure_structure()
    session_dir = get_session_dir()

    # Create IOC record
    ioc_record = {
        "ioc_id": f"IOC_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "value": ioc_value,
        "type": ioc_type,
        "source": ioc_source,
        "investigation_id": investigation_id,
        "discovery_time": datetime.now(datetime.UTC).isoformat(),
        "confidence": calculate_ioc_confidence(ioc_type, ioc_value, ioc_source),
        "threat_level": assess_threat_level(ioc_type, ioc_value),
        "investigator": os.environ.get('USER', 'unknown'),
        "context": extract_ioc_context(ioc_type, ioc_value),
        "enrichment": await enrich_ioc(ioc_type, ioc_value),
        "mitre_mapping": get_ioc_mitre_mapping(ioc_type, ioc_value),
        "attribution": assess_ioc_attribution(ioc_type, ioc_value)
    }

    # Save IOC record
    if session_dir:
        investigation_dir = session_dir / investigation_id
        iocs_dir = investigation_dir / "iocs"
        iocs_dir.mkdir(parents=True, exist_ok=True)

        # Save to type-specific file
        ioc_type_file = iocs_dir / f"{ioc_type.lower()}_iocs.json"
        await append_ioc_to_file(ioc_type_file, ioc_record)

        # Save individual IOC record
        ioc_file = iocs_dir / f"ioc_{ioc_record['ioc_id']}.json"
        ioc_file.write_text(json.dumps(ioc_record, indent=2))

        # Update investigation timeline
        await update_ioc_timeline(investigation_dir, ioc_record)

        # Check for IOC correlations
        correlations = await find_ioc_correlations(iocs_dir, ioc_record)
        if correlations:
            ioc_record["correlations"] = correlations

    # Determine IOC priority
    priority = determine_ioc_priority(ioc_record)

    # Generate output for Claude
    output = {
        "hookSpecificOutput": {
            "additionalContext": f"""🔍 **IOC DISCOVERED - {priority.upper()} PRIORITY**

📊 **IOC Information:**
• IOC ID: {ioc_record['ioc_id']}
• Type: {ioc_type}
• Value: {ioc_value}
• Source: {ioc_source}
• Discovery Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚡ **Assessment:**
• Confidence: {ioc_record['confidence']:.1%}
• Threat Level: {ioc_record['threat_level'].upper()}
• Priority: {priority}

🎯 **IOC Context:**
{format_ioc_context(ioc_record['context'])}

🔬 **Threat Intelligence:**
{format_ioc_enrichment(ioc_record['enrichment'])}

🏛️ **MITRE ATT&CK Mapping:**
{format_mitre_mapping(ioc_record['mitre_mapping'])}

🔗 **Attribution Analysis:**
{format_attribution_analysis(ioc_record['attribution'])}

📋 **Investigation Actions:**
{format_ioc_investigation_actions(ioc_type, ioc_record['threat_level'])}

{format_correlation_info(ioc_record.get('correlations', []))}

**IOC documented and added to threat intelligence database.**"""
        }
    }

    print(json.dumps(output))


def calculate_ioc_confidence(ioc_type, ioc_value, source):
    """Calculate confidence score for IOC"""

    base_confidence = {
        "network_scan": 0.7,
        "file_analysis": 0.8,
        "process_monitoring": 0.9,
        "memory_analysis": 0.95,
        "manual_investigation": 0.6,
        "automated_detection": 0.8
    }

    confidence = base_confidence.get(source, 0.5)

    # Adjust based on IOC type
    type_modifiers = {
        "file_hash": 0.1,      # High confidence for hashes
        "process_name": 0.05,  # Good confidence for processes
        "ip_address": 0.0,     # Neutral for IPs
        "domain": 0.0,         # Neutral for domains
        "url": -0.1,           # Lower confidence for URLs
        "registry_key": 0.05,  # Good for registry
        "file_path": -0.05,    # Slightly lower for paths
    }

    confidence += type_modifiers.get(ioc_type.lower(), 0.0)

    # Adjust based on value characteristics
    if len(ioc_value) > 50:  # Long values tend to be more specific
        confidence += 0.05
    if any(char in ioc_value for char in ['/', '\\', ':']):  # Structured values
        confidence += 0.05

    return min(max(confidence, 0.0), 1.0)  # Clamp to 0-1 range


def assess_threat_level(ioc_type, ioc_value):
    """Assess threat level based on IOC characteristics"""

    # High-threat patterns
    high_threat_patterns = [
        "mimikatz", "psexec", "powershell.exe -enc", "cmd.exe /c",
        "certutil -decode", "regsvr32 /s", "rundll32.exe",
        "krbtgt", "administrator", "lsass.exe"
    ]

    # Medium-threat patterns
    medium_threat_patterns = [
        "temp", "tmp", "appdata", "programdata",
        "system32", "syswow64", "windows", "users"
    ]

    value_lower = ioc_value.lower()

    # Check for high-threat patterns
    if any(pattern in value_lower for pattern in high_threat_patterns):
        return "high"

    # Check IOC type threats
    high_threat_types = ["process_name", "file_hash", "registry_key"]
    if ioc_type.lower() in high_threat_types:
        return "medium"

    # Check for medium-threat patterns
    if any(pattern in value_lower for pattern in medium_threat_patterns):
        return "medium"

    # Check for suspicious characteristics
    if any(char in value_lower for char in ['%', '$', '@', '&']):
        return "medium"

    return "low"


def extract_ioc_context(ioc_type, ioc_value):
    """Extract contextual information about the IOC"""

    context = {
        "characteristics": [],
        "location_hints": [],
        "behavioral_indicators": []
    }

    value_lower = ioc_value.lower()

    # Analyze characteristics
    if len(ioc_value) == 32:
        context["characteristics"].append("MD5 hash length")
    elif len(ioc_value) == 40:
        context["characteristics"].append("SHA1 hash length")
    elif len(ioc_value) == 64:
        context["characteristics"].append("SHA256 hash length")

    # Location hints
    if any(loc in value_lower for loc in ["temp", "tmp", "appdata"]):
        context["location_hints"].append("Temporary location")
    if any(loc in value_lower for loc in ["system32", "syswow64"]):
        context["location_hints"].append("System directory")
    if any(loc in value_lower for loc in ["programdata", "program files"]):
        context["location_hints"].append("Program installation area")

    # Behavioral indicators
    if any(behavior in value_lower for behavior in ["download", "upload", "connect"]):
        context["behavioral_indicators"].append("Network activity")
    if any(behavior in value_lower for behavior in ["execute", "run", "start"]):
        context["behavioral_indicators"].append("Execution activity")
    if any(behavior in value_lower for behavior in ["copy", "move", "delete"]):
        context["behavioral_indicators"].append("File manipulation")

    return context


async def enrich_ioc(ioc_type, ioc_value):
    """Enrich IOC with threat intelligence"""

    enrichment = {
        "threat_intelligence": [],
        "known_campaigns": [],
        "related_malware": [],
        "first_seen": None,
        "reputation": "unknown"
    }

    # Simulate threat intelligence enrichment
    # In a real implementation, this would query threat intelligence feeds

    value_lower = ioc_value.lower()

    # Check for known malware indicators
    known_malware = {
        "mimikatz": {
            "family": "Credential Dumper",
            "campaigns": ["APT29", "APT28", "Various"],
            "first_seen": "2014-01-01"
        },
        "psexec": {
            "family": "Remote Execution Tool",
            "campaigns": ["Legitimate Admin Tool", "APT Usage"],
            "first_seen": "2005-01-01"
        },
        "krbtgt": {
            "family": "Kerberos Target",
            "campaigns": ["Golden Ticket Attacks"],
            "first_seen": "2015-01-01"
        }
    }

    for malware, info in known_malware.items():
        if malware in value_lower:
            enrichment["related_malware"].append(info["family"])
            enrichment["known_campaigns"].extend(info["campaigns"])
            enrichment["first_seen"] = info["first_seen"]
            enrichment["reputation"] = "malicious"
            break

    # Domain/IP reputation (simplified)
    if ioc_type.lower() in ["domain", "ip_address", "url"]:
        suspicious_tlds = [".tk", ".ml", ".ga", ".cf", ".bit"]
        if any(tld in value_lower for tld in suspicious_tlds):
            enrichment["reputation"] = "suspicious"
            enrichment["threat_intelligence"].append("Suspicious TLD usage")

    return enrichment


def get_ioc_mitre_mapping(ioc_type, ioc_value):
    """Map IOC to MITRE ATT&CK techniques"""

    value_lower = ioc_value.lower()

    # IOC to MITRE mapping patterns
    mitre_patterns = {
        "mimikatz": {
            "techniques": ["T1558.003", "T1003.001"],  # Kerberoasting, LSASS
            "tactics": ["TA0006"],  # Credential Access
            "description": "Credential dumping tool"
        },
        "psexec": {
            "techniques": ["T1021.002"],  # SMB/Windows Admin Shares
            "tactics": ["TA0008"],  # Lateral Movement
            "description": "Remote execution tool"
        },
        "krbtgt": {
            "techniques": ["T1558.001"],  # Golden Ticket
            "tactics": ["TA0006"],  # Credential Access
            "description": "Kerberos ticket manipulation"
        },
        "powershell": {
            "techniques": ["T1059.001"],  # PowerShell
            "tactics": ["TA0002"],  # Execution
            "description": "PowerShell execution"
        },
        "cmd.exe": {
            "techniques": ["T1059.003"],  # Windows Command Shell
            "tactics": ["TA0002"],  # Execution
            "description": "Command line execution"
        },
        "lsass": {
            "techniques": ["T1003.001"],  # LSASS Memory
            "tactics": ["TA0006"],  # Credential Access
            "description": "Memory credential dumping"
        }
    }

    # Check for pattern matches
    for pattern, mapping in mitre_patterns.items():
        if pattern in value_lower:
            return mapping

    # Default mapping based on IOC type
    type_mappings = {
        "process_name": {
            "techniques": ["T1055"],  # Process Injection
            "tactics": ["TA0005"],  # Defense Evasion
            "description": "Process-based activity"
        },
        "file_hash": {
            "techniques": ["T1027"],  # Obfuscated Files or Information
            "tactics": ["TA0005"],  # Defense Evasion
            "description": "File-based indicator"
        },
        "network": {
            "techniques": ["T1071"],  # Application Layer Protocol
            "tactics": ["TA0011"],  # Command and Control
            "description": "Network-based indicator"
        }
    }

    ioc_category = categorize_ioc_type(ioc_type)
    return type_mappings.get(ioc_category, {
        "techniques": ["T1082"],  # System Information Discovery
        "tactics": ["TA0007"],  # Discovery
        "description": "General indicator"
    })


def assess_ioc_attribution(ioc_type, ioc_value):
    """Assess potential attribution for IOC"""

    attribution = {
        "confidence": 0.0,
        "potential_actors": [],
        "campaign_indicators": [],
        "geographic_indicators": []
    }

    value_lower = ioc_value.lower()

    # Known APT tool indicators
    apt_tools = {
        "mimikatz": ["APT29", "APT28", "Lazarus", "FIN7"],
        "psexec": ["APT1", "APT29", "APT28"],
        "powershell": ["APT29", "APT28", "FIN7", "Carbanak"]
    }

    for tool, actors in apt_tools.items():
        if tool in value_lower:
            attribution["potential_actors"].extend(actors)
            attribution["confidence"] = 0.3  # Low confidence for common tools
            break

    # Language/locale indicators
    if any(lang in value_lower for lang in ["ru", "rus", "russian"]):
        attribution["geographic_indicators"].append("Russian-speaking")
        attribution["confidence"] += 0.2
    elif any(lang in value_lower for lang in ["cn", "china", "chinese"]):
        attribution["geographic_indicators"].append("Chinese-speaking")
        attribution["confidence"] += 0.2

    # Campaign naming patterns
    if any(pattern in value_lower for pattern in ["cozy", "bear", "fancy"]):
        attribution["campaign_indicators"].append("Bear campaign naming")
        attribution["potential_actors"].extend(["APT29", "APT28"])
        attribution["confidence"] = 0.4

    return attribution


def categorize_ioc_type(ioc_type):
    """Categorize IOC type for processing"""
    network_types = ["ip_address", "domain", "url", "network"]
    file_types = ["file_hash", "file_path", "file_name"]
    process_types = ["process_name", "service_name"]

    if any(t in ioc_type.lower() for t in network_types):
        return "network"
    elif any(t in ioc_type.lower() for t in file_types):
        return "file"
    elif any(t in ioc_type.lower() for t in process_types):
        return "process"
    else:
        return "other"


def determine_ioc_priority(ioc_record):
    """Determine priority level for IOC"""

    confidence = ioc_record["confidence"]
    threat_level = ioc_record["threat_level"]
    attribution_conf = ioc_record["attribution"]["confidence"]

    # Priority matrix
    if threat_level == "high" and confidence > 0.8:
        return "CRITICAL"
    elif threat_level == "high" and confidence > 0.6:
        return "HIGH"
    elif threat_level == "medium" and confidence > 0.7:
        return "HIGH"
    elif threat_level == "medium" and confidence > 0.5:
        return "MEDIUM"
    else:
        return "LOW"


async def append_ioc_to_file(ioc_file, ioc_record):
    """Append IOC to type-specific file"""

    iocs = []
    if ioc_file.exists():
        try:
            iocs = json.loads(ioc_file.read_text())
        except:
            iocs = []

    iocs.append(ioc_record)
    ioc_file.write_text(json.dumps(iocs, indent=2))


async def find_ioc_correlations(iocs_dir, new_ioc):
    """Find correlations with existing IOCs"""

    correlations = []

    # Check all existing IOC files
    for ioc_file in iocs_dir.glob("*.json"):
        if ioc_file.name.startswith("ioc_"):
            continue  # Skip individual IOC files

        try:
            existing_iocs = json.loads(ioc_file.read_text())
            if isinstance(existing_iocs, list):
                for existing_ioc in existing_iocs:
                    correlation = check_ioc_correlation(new_ioc, existing_ioc)
                    if correlation:
                        correlations.append(correlation)
        except:
            continue

    return correlations[:5]  # Return top 5 correlations


def check_ioc_correlation(ioc1, ioc2):
    """Check if two IOCs are correlated"""

    correlation_score = 0.0
    correlation_factors = []

    # Same source correlation
    if ioc1["source"] == ioc2["source"]:
        correlation_score += 0.3
        correlation_factors.append("Same detection source")

    # Temporal correlation (within 1 hour)
    try:
        time1 = datetime.fromisoformat(ioc1["discovery_time"].replace('Z', '+00:00'))
        time2 = datetime.fromisoformat(ioc2["discovery_time"].replace('Z', '+00:00'))
        time_diff = abs((time1 - time2).total_seconds())

        if time_diff < 3600:  # 1 hour
            correlation_score += 0.4
            correlation_factors.append("Temporal proximity")
    except:
        pass

    # MITRE technique correlation
    mitre1 = set(ioc1.get("mitre_mapping", {}).get("techniques", []))
    mitre2 = set(ioc2.get("mitre_mapping", {}).get("techniques", []))
    if mitre1.intersection(mitre2):
        correlation_score += 0.3
        correlation_factors.append("Shared MITRE techniques")

    # Attribution correlation
    attr1 = set(ioc1.get("attribution", {}).get("potential_actors", []))
    attr2 = set(ioc2.get("attribution", {}).get("potential_actors", []))
    if attr1.intersection(attr2):
        correlation_score += 0.2
        correlation_factors.append("Shared potential actors")

    # Return correlation if significant
    if correlation_score >= 0.5:
        return {
            "correlated_ioc": ioc2["ioc_id"],
            "correlation_score": correlation_score,
            "correlation_factors": correlation_factors
        }

    return None


async def update_ioc_timeline(investigation_dir, ioc_record):
    """Update investigation timeline with IOC discovery"""

    timeline_file = investigation_dir / "timeline" / "investigation_timeline.json"
    timeline_file.parent.mkdir(exist_ok=True)

    timeline_entry = {
        "timestamp": datetime.now(datetime.UTC).isoformat(),
        "event_type": "ioc_discovered",
        "ioc_id": ioc_record["ioc_id"],
        "ioc_type": ioc_record["type"],
        "ioc_value": ioc_record["value"],
        "confidence": ioc_record["confidence"],
        "threat_level": ioc_record["threat_level"],
        "metadata": ioc_record
    }

    # Load existing timeline or create new
    timeline = []
    if timeline_file.exists():
        try:
            timeline = json.loads(timeline_file.read_text())
        except:
            timeline = []

    timeline.append(timeline_entry)
    timeline_file.write_text(json.dumps(timeline, indent=2))


def format_ioc_context(context):
    """Format IOC context for display"""
    if not context:
        return "• Context analysis pending"

    formatted = []

    characteristics = context.get("characteristics", [])
    if characteristics:
        formatted.append(f"• Characteristics: {', '.join(characteristics[:3])}")

    location_hints = context.get("location_hints", [])
    if location_hints:
        formatted.append(f"• Location Hints: {', '.join(location_hints[:2])}")

    behavioral = context.get("behavioral_indicators", [])
    if behavioral:
        formatted.append(f"• Behavioral: {', '.join(behavioral[:2])}")

    return "\n".join(formatted) if formatted else "• No contextual indicators identified"


def format_ioc_enrichment(enrichment):
    """Format IOC enrichment for display"""
    if not enrichment:
        return "• Threat intelligence enrichment pending"

    formatted = []

    reputation = enrichment.get("reputation", "unknown")
    formatted.append(f"• Reputation: {reputation.upper()}")

    malware = enrichment.get("related_malware", [])
    if malware:
        formatted.append(f"• Related Malware: {', '.join(malware[:2])}")

    campaigns = enrichment.get("known_campaigns", [])
    if campaigns:
        formatted.append(f"• Known Campaigns: {', '.join(campaigns[:3])}")

    intel = enrichment.get("threat_intelligence", [])
    if intel:
        formatted.append(f"• Intelligence: {intel[0]}")

    return "\n".join(formatted) if formatted else "• No threat intelligence available"


def format_mitre_mapping(mapping):
    """Format MITRE mapping for display"""
    if not mapping:
        return "• MITRE mapping pending"

    techniques = ", ".join(mapping.get("techniques", []))
    tactics = ", ".join(mapping.get("tactics", []))
    description = mapping.get("description", "Unknown")

    return f"""• Techniques: {techniques}
• Tactics: {tactics}
• Description: {description}"""


def format_attribution_analysis(attribution):
    """Format attribution analysis for display"""
    if not attribution:
        return "• Attribution analysis pending"

    confidence = attribution.get("confidence", 0.0)
    actors = attribution.get("potential_actors", [])
    geo_indicators = attribution.get("geographic_indicators", [])

    formatted = [f"• Confidence: {confidence:.1%}"]

    if actors:
        formatted.append(f"• Potential Actors: {', '.join(actors[:3])}")

    if geo_indicators:
        formatted.append(f"• Geographic: {', '.join(geo_indicators)}")

    return "\n".join(formatted)


def format_ioc_investigation_actions(ioc_type, threat_level):
    """Format investigation actions for IOC"""

    actions = [
        "Cross-reference with existing IOC database",
        "Update threat intelligence feeds",
        "Monitor for additional related indicators"
    ]

    type_actions = {
        "process_name": [
            "Analyze process behavior and memory",
            "Check for process injection patterns"
        ],
        "file_hash": [
            "Perform static malware analysis",
            "Check file distribution and variants"
        ],
        "ip_address": [
            "Monitor network traffic to/from IP",
            "Analyze geolocation and infrastructure"
        ],
        "domain": [
            "Monitor DNS queries and resolutions",
            "Analyze domain registration data"
        ]
    }

    category = categorize_ioc_type(ioc_type)
    actions.extend(type_actions.get(category, []))

    if threat_level in ["high", "critical"]:
        actions.extend([
            "Implement blocking/containment measures",
            "Notify security operations center"
        ])

    return "\n".join(f"• {action}" for action in actions[:5])


def format_correlation_info(correlations):
    """Format correlation information"""
    if not correlations:
        return ""

    correlation_count = len(correlations)
    top_correlation = max(correlations, key=lambda x: x["correlation_score"])

    return f"""
🔗 **IOC Correlations ({correlation_count} found):**
• Top Correlation: {top_correlation['correlated_ioc']} (Score: {top_correlation['correlation_score']:.1%})
• Factors: {', '.join(top_correlation['correlation_factors'][:2])}"""


def main():
    """Entry point with uvloop optimization"""
    run_with_uvloop(ioc_discovered_async())


if __name__ == "__main__":
    main()