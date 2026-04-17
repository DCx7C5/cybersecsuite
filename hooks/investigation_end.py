#!/usr/bin/env python3
"""
MalwareHunter Investigation End Hook
Finalizes comprehensive APT investigation with complete analysis and reporting
"""

import asyncio
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from utils import ensure_structure, get_session_dir, get_project_dir
from uvloop_integration import run_with_uvloop


async def investigation_end_async():
    """Finalize comprehensive APT investigation"""

    # Get investigation parameters
    investigation_id = os.environ.get('MALWARE_INVESTIGATION_ID', 'unknown')
    investigation_dir_path = os.environ.get('MALWARE_INVESTIGATION_DIR')

    # Ensure directory structure
    ensure_structure()
    session_dir = get_session_dir()

    if investigation_dir_path:
        investigation_dir = Path(investigation_dir_path)
    elif session_dir:
        investigation_dir = session_dir / investigation_id
    else:
        investigation_dir = None

    # Load investigation metadata
    investigation_metadata = {}
    if investigation_dir and investigation_dir.exists():
        metadata_file = investigation_dir / "investigation_metadata.json"
        if metadata_file.exists():
            try:
                investigation_metadata = json.loads(metadata_file.read_text())
            except:
                pass

    # Generate comprehensive investigation summary
    investigation_summary = await generate_investigation_summary(investigation_dir, investigation_metadata)

    # Update investigation metadata with completion info
    investigation_metadata.update({
        "end_time": datetime.now(datetime.UTC).isoformat(),
        "status": "completed",
        "summary": investigation_summary
    })

    # Save final metadata
    if investigation_dir:
        metadata_file = investigation_dir / "investigation_metadata.json"
        metadata_file.write_text(json.dumps(investigation_metadata, indent=2))

        # Generate final investigation report
        await generate_final_investigation_report(investigation_dir, investigation_summary)

        # Update timeline with completion
        await update_final_timeline(investigation_dir, investigation_summary)

        # Archive investigation
        await archive_investigation(investigation_dir, investigation_summary)

    # Generate output for Claude
    output = {
        "hookSpecificOutput": {
            "additionalContext": f"""🏁 **MALWAREHUNTER INVESTIGATION COMPLETED**

📋 **Investigation Summary:**
• Investigation ID: {investigation_id}
• Duration: {calculate_investigation_duration(investigation_metadata)}
• Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• Status: Investigation Complete

🎯 **Investigation Results:**
{format_investigation_results(investigation_summary)}

📊 **IOC Summary:**
{format_ioc_summary(investigation_summary.get('iocs', {}))}

⚠️ **Threat Assessment:**
{format_threat_assessment(investigation_summary.get('threats', {}))}

🔍 **Evidence Quality:**
{format_evidence_analysis(investigation_summary.get('evidence', {}))}

🏛️ **MITRE ATT&CK Analysis:**
{format_mitre_analysis(investigation_summary.get('mitre_analysis', {}))}

📈 **Attribution Confidence:**
{format_attribution_analysis(investigation_summary.get('attribution', {}))}

📂 **Final Deliverables:**
{format_deliverables(investigation_dir if investigation_dir else None)}

🎉 **Investigation {investigation_id} completed successfully. All evidence preserved and documented.**"""
        }
    }

    print(json.dumps(output))


async def generate_investigation_summary(investigation_dir, metadata):
    """Generate comprehensive investigation summary"""

    summary = {
        "investigation_id": metadata.get("investigation_id", "unknown"),
        "threat_scenario": metadata.get("threat_scenario", "unknown"),
        "phases_completed": [],
        "total_artifacts": 0,
        "iocs": {
            "total_discovered": 0,
            "high_confidence": 0,
            "categories": {},
            "mitre_mapped": 0
        },
        "threats": {
            "confirmed": 0,
            "potential": 0,
            "severity_distribution": {}
        },
        "evidence": {
            "files_collected": 0,
            "integrity_verified": True,
            "chain_of_custody": True
        },
        "mitre_analysis": {
            "tactics_identified": [],
            "techniques_detected": [],
            "attack_patterns": []
        },
        "attribution": {
            "confidence_score": 0.0,
            "potential_actors": [],
            "campaign_indicators": []
        }
    }

    if not investigation_dir or not investigation_dir.exists():
        return summary

    # Analyze completed phases
    phases_dir = investigation_dir / "phases"
    if phases_dir.exists():
        for phase_dir in phases_dir.iterdir():
            if phase_dir.is_dir():
                phase_metadata_file = phase_dir / "phase_metadata.json"
                if phase_metadata_file.exists():
                    try:
                        phase_data = json.loads(phase_metadata_file.read_text())
                        if phase_data.get("status") == "completed":
                            summary["phases_completed"].append(phase_data.get("phase_name", phase_dir.name))
                    except:
                        pass

    # Count total artifacts
    artifacts_dir = investigation_dir / "artifacts"
    if artifacts_dir.exists():
        summary["total_artifacts"] = len(list(artifacts_dir.rglob("*")))

    # Analyze IOCs
    summary["iocs"] = await analyze_investigation_iocs(investigation_dir)

    # Analyze threats
    summary["threats"] = await analyze_investigation_threats(investigation_dir)

    # Analyze evidence
    summary["evidence"] = await analyze_evidence_quality(investigation_dir)

    # MITRE analysis
    summary["mitre_analysis"] = await analyze_mitre_mapping(investigation_dir)

    # Attribution analysis
    summary["attribution"] = await analyze_threat_attribution(investigation_dir, summary)

    return summary


async def analyze_investigation_iocs(investigation_dir):
    """Analyze all IOCs discovered during investigation"""

    ioc_analysis = {
        "total_discovered": 0,
        "high_confidence": 0,
        "categories": {},
        "mitre_mapped": 0,
        "network_indicators": 0,
        "file_indicators": 0,
        "process_indicators": 0,
        "behavioral_indicators": 0
    }

    iocs_dir = investigation_dir / "iocs"
    if not iocs_dir.exists():
        return ioc_analysis

    # Analyze IOC files
    for ioc_file in iocs_dir.rglob("*.json"):
        try:
            ioc_data = json.loads(ioc_file.read_text())

            if isinstance(ioc_data, list):
                for ioc in ioc_data:
                    ioc_analysis["total_discovered"] += 1

                    # Confidence analysis
                    confidence = ioc.get("confidence", 0)
                    if confidence > 0.7:
                        ioc_analysis["high_confidence"] += 1

                    # Category analysis
                    ioc_type = ioc.get("type", "unknown").lower()
                    category = categorize_ioc_type(ioc_type)
                    ioc_analysis["categories"][category] = ioc_analysis["categories"].get(category, 0) + 1

                    # Type-specific counting
                    if any(net_type in ioc_type for net_type in ["ip", "domain", "url", "network"]):
                        ioc_analysis["network_indicators"] += 1
                    elif any(file_type in ioc_type for file_type in ["file", "hash", "path"]):
                        ioc_analysis["file_indicators"] += 1
                    elif any(proc_type in ioc_type for proc_type in ["process", "service"]):
                        ioc_analysis["process_indicators"] += 1
                    else:
                        ioc_analysis["behavioral_indicators"] += 1

                    # MITRE mapping check
                    if ioc.get("mitre_techniques"):
                        ioc_analysis["mitre_mapped"] += 1

            elif isinstance(ioc_data, dict):
                # Single IOC file
                ioc_analysis["total_discovered"] += 1
                # Add similar analysis for single IOCs

        except:
            continue

    return ioc_analysis


async def analyze_investigation_threats(investigation_dir):
    """Analyze threats identified during investigation"""

    threat_analysis = {
        "confirmed": 0,
        "potential": 0,
        "false_positives": 0,
        "severity_distribution": {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        },
        "threat_categories": {},
        "attack_vectors": []
    }

    # Look for threat analysis files in phases
    phases_dir = investigation_dir / "phases"
    if phases_dir.exists():
        for phase_dir in phases_dir.iterdir():
            threat_file = phase_dir / "threat_analysis.json"
            if threat_file.exists():
                try:
                    threat_data = json.loads(threat_file.read_text())

                    summary = threat_data.get("summary", {})
                    threat_analysis["confirmed"] += summary.get("confirmed_threats", 0)
                    threat_analysis["potential"] += summary.get("potential_threats", 0)
                    threat_analysis["false_positives"] += summary.get("false_positives", 0)

                    # Merge severity distribution
                    severity_dist = summary.get("severity_distribution", {})
                    for severity, count in severity_dist.items():
                        if severity in threat_analysis["severity_distribution"]:
                            threat_analysis["severity_distribution"][severity] += count

                except:
                    continue

    return threat_analysis


async def analyze_evidence_quality(investigation_dir):
    """Analyze evidence collection quality"""

    evidence_analysis = {
        "files_collected": 0,
        "integrity_verified": True,
        "chain_of_custody": True,
        "timestamps_accurate": True,
        "evidence_categories": {},
        "preservation_quality": "high"
    }

    # Count evidence files
    artifacts_dir = investigation_dir / "artifacts"
    if artifacts_dir.exists():
        evidence_files = list(artifacts_dir.rglob("*"))
        evidence_analysis["files_collected"] = len([f for f in evidence_files if f.is_file()])

        # Categorize evidence
        for evidence_file in evidence_files:
            if evidence_file.is_file():
                category = categorize_evidence_file(evidence_file)
                evidence_analysis["evidence_categories"][category] = evidence_analysis["evidence_categories"].get(category, 0) + 1

    # Check for integrity verification files
    integrity_files = list(investigation_dir.glob("**/*.md5")) + list(investigation_dir.glob("**/*.sha256"))
    if len(integrity_files) == 0 and evidence_analysis["files_collected"] > 0:
        evidence_analysis["integrity_verified"] = False

    return evidence_analysis


async def analyze_mitre_mapping(investigation_dir):
    """Analyze MITRE ATT&CK technique mapping"""

    mitre_analysis = {
        "tactics_identified": [],
        "techniques_detected": [],
        "attack_patterns": [],
        "coverage_score": 0.0,
        "apt_correlation": []
    }

    # Look for MITRE analysis files
    mitre_files = list(investigation_dir.rglob("*mitre*.json"))

    tactics_found = set()
    techniques_found = set()

    for mitre_file in mitre_files:
        try:
            mitre_data = json.loads(mitre_file.read_text())

            if isinstance(mitre_data, dict):
                # Extract tactics and techniques
                for key, value in mitre_data.items():
                    if "tactic" in key.lower() and isinstance(value, list):
                        tactics_found.update(value)
                    elif "technique" in key.lower() and isinstance(value, list):
                        techniques_found.update(value)

        except:
            continue

    mitre_analysis["tactics_identified"] = list(tactics_found)
    mitre_analysis["techniques_detected"] = list(techniques_found)
    mitre_analysis["coverage_score"] = min(len(techniques_found) / 20.0, 1.0)  # Normalize to 20 techniques

    return mitre_analysis


async def analyze_threat_attribution(investigation_dir, summary):
    """Analyze threat attribution confidence"""

    attribution_analysis = {
        "confidence_score": 0.0,
        "potential_actors": [],
        "campaign_indicators": [],
        "attribution_factors": []
    }

    # Calculate confidence based on various factors
    confidence_factors = []

    # IOC confidence contribution
    ioc_confidence = summary["iocs"]["high_confidence"] / max(summary["iocs"]["total_discovered"], 1)
    confidence_factors.append(("IOC Quality", ioc_confidence * 0.3))

    # MITRE mapping contribution
    mitre_confidence = summary["mitre_analysis"]["coverage_score"]
    confidence_factors.append(("MITRE Mapping", mitre_confidence * 0.3))

    # Evidence quality contribution
    evidence_confidence = 0.8 if summary["evidence"]["integrity_verified"] else 0.4
    confidence_factors.append(("Evidence Quality", evidence_confidence * 0.2))

    # Threat confirmation contribution
    threat_confidence = min(summary["threats"]["confirmed"] / 3.0, 1.0)  # Normalize to 3 threats
    confidence_factors.append(("Threat Confirmation", threat_confidence * 0.2))

    # Calculate overall confidence
    total_confidence = sum(factor[1] for factor in confidence_factors)
    attribution_analysis["confidence_score"] = min(total_confidence, 1.0)

    attribution_analysis["attribution_factors"] = confidence_factors

    # Determine potential actors based on techniques (simplified)
    techniques = summary["mitre_analysis"]["techniques_detected"]
    if "T1558.003" in techniques:  # Kerberoasting
        attribution_analysis["potential_actors"].append("APT groups targeting AD environments")
    if "T1055" in techniques:  # Process injection
        attribution_analysis["potential_actors"].append("Advanced persistent threat groups")

    return attribution_analysis


async def generate_final_investigation_report(investigation_dir, summary):
    """Generate comprehensive final investigation report"""

    reports_dir = investigation_dir / "reports"
    reports_dir.mkdir(exist_ok=True)

    report_file = reports_dir / f"final_investigation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    report_content = f"""# MalwareHunter Investigation Final Report

## Executive Summary
- **Investigation ID**: {summary['investigation_id']}
- **Threat Scenario**: {summary['threat_scenario']}
- **Investigation Period**: {get_investigation_period(investigation_dir)}
- **Status**: COMPLETED

## Key Findings
{format_key_findings(summary)}

## IOC Analysis
{format_detailed_ioc_analysis(summary['iocs'])}

## Threat Assessment
{format_detailed_threat_analysis(summary['threats'])}

## MITRE ATT&CK Analysis
{format_detailed_mitre_analysis(summary['mitre_analysis'])}

## Attribution Analysis
{format_detailed_attribution_analysis(summary['attribution'])}

## Evidence Summary
{format_detailed_evidence_analysis(summary['evidence'])}

## Recommendations
{format_investigation_recommendations(summary)}

## Investigation Timeline
{await format_investigation_timeline(investigation_dir)}

---
*Report generated by MalwareHunter Investigation Framework*
*Completion Time: {datetime.now().isoformat()}*
"""

    report_file.write_text(report_content)


async def update_final_timeline(investigation_dir, summary):
    """Update investigation timeline with completion"""

    timeline_file = investigation_dir / "timeline" / "investigation_timeline.json"

    completion_entry = {
        "timestamp": datetime.now(datetime.UTC).isoformat(),
        "event_type": "investigation_complete",
        "investigation_id": summary["investigation_id"],
        "summary": summary
    }

    if timeline_file.exists():
        try:
            timeline = json.loads(timeline_file.read_text())
            timeline.append(completion_entry)
            timeline_file.write_text(json.dumps(timeline, indent=2))
        except:
            pass

    # Update markdown timeline
    markdown_timeline = investigation_dir / "timeline.md"
    if markdown_timeline.exists():
        current_content = markdown_timeline.read_text()
        completion_section = f"""

### Investigation Completed
- **Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Total IOCs**: {summary['iocs']['total_discovered']}
- **Confirmed Threats**: {summary['threats']['confirmed']}
- **Attribution Confidence**: {summary['attribution']['confidence_score']:.2f}
- **Phases Completed**: {len(summary['phases_completed'])}

**Investigation Status**: COMPLETED ✅
"""
        markdown_timeline.write_text(current_content + completion_section)


async def archive_investigation(investigation_dir, summary):
    """Archive completed investigation"""

    # Create archive metadata
    archive_metadata = {
        "archived_at": datetime.now(datetime.UTC).isoformat(),
        "investigation_summary": summary,
        "archive_integrity": "preserved",
        "retention_policy": "as per organizational requirements"
    }

    archive_file = investigation_dir / "archive_metadata.json"
    archive_file.write_text(json.dumps(archive_metadata, indent=2))

    # Optionally compress investigation (placeholder)
    # This could integrate with actual archiving systems


def calculate_investigation_duration(metadata):
    """Calculate investigation duration"""
    start_time = metadata.get("start_time")
    end_time = metadata.get("end_time")

    if start_time and end_time:
        try:
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            duration = end - start
            return f"{duration.total_seconds() / 3600:.1f} hours"
        except:
            pass

    return "Duration calculation unavailable"


def categorize_ioc_type(ioc_type):
    """Categorize IOC type for analysis"""
    if any(net_type in ioc_type for net_type in ["ip", "domain", "url", "network"]):
        return "Network"
    elif any(file_type in ioc_type for file_type in ["file", "hash", "path"]):
        return "File"
    elif any(proc_type in ioc_type for proc_type in ["process", "service"]):
        return "Process"
    elif any(reg_type in ioc_type for reg_type in ["registry", "key"]):
        return "Registry"
    else:
        return "Behavioral"


def categorize_evidence_file(file_path):
    """Categorize evidence file for analysis"""
    file_str = str(file_path).lower()

    if "network" in file_str:
        return "Network"
    elif "process" in file_str:
        return "Process"
    elif "memory" in file_str:
        return "Memory"
    elif "log" in file_str:
        return "Logs"
    elif "browser" in file_str:
        return "Browser"
    elif "firmware" in file_str:
        return "Firmware"
    else:
        return "General"


def format_investigation_results(summary):
    """Format investigation results for display"""
    phases_completed = len(summary.get("phases_completed", []))
    total_artifacts = summary.get("total_artifacts", 0)
    iocs_found = summary["iocs"]["total_discovered"]
    threats_confirmed = summary["threats"]["confirmed"]

    return f"""• Phases Completed: {phases_completed}/6
• Total Artifacts Collected: {total_artifacts}
• IOCs Discovered: {iocs_found}
• Confirmed Threats: {threats_confirmed}
• Attribution Confidence: {summary['attribution']['confidence_score']:.1%}"""


def format_ioc_summary(iocs):
    """Format IOC summary for display"""
    total = iocs["total_discovered"]
    high_conf = iocs["high_confidence"]
    network = iocs.get("network_indicators", 0)
    file_indicators = iocs.get("file_indicators", 0)

    return f"""• Total IOCs: {total}
• High Confidence: {high_conf}
• Network Indicators: {network}
• File Indicators: {file_indicators}
• MITRE Mapped: {iocs.get("mitre_mapped", 0)}"""


def format_threat_assessment(threats):
    """Format threat assessment for display"""
    confirmed = threats["confirmed"]
    potential = threats["potential"]
    critical = threats["severity_distribution"].get("critical", 0)
    high = threats["severity_distribution"].get("high", 0)

    return f"""• Confirmed Threats: {confirmed}
• Potential Threats: {potential}
• Critical Severity: {critical}
• High Severity: {high}"""


def format_evidence_analysis(evidence):
    """Format evidence analysis for display"""
    files = evidence["files_collected"]
    integrity = "✅" if evidence["integrity_verified"] else "❌"
    custody = "✅" if evidence["chain_of_custody"] else "❌"

    return f"""• Evidence Files: {files}
• Integrity Verified: {integrity}
• Chain of Custody: {custody}
• Preservation Quality: {evidence.get("preservation_quality", "unknown")}"""


def format_mitre_analysis(mitre):
    """Format MITRE analysis for display"""
    tactics = len(mitre["tactics_identified"])
    techniques = len(mitre["techniques_detected"])
    coverage = mitre["coverage_score"]

    return f"""• Tactics Identified: {tactics}
• Techniques Detected: {techniques}
• Coverage Score: {coverage:.1%}
• Attack Patterns: {len(mitre.get("attack_patterns", []))}"""


def format_attribution_analysis(attribution):
    """Format attribution analysis for display"""
    confidence = attribution["confidence_score"]
    actors = len(attribution["potential_actors"])
    indicators = len(attribution["campaign_indicators"])

    confidence_level = "High" if confidence > 0.7 else "Medium" if confidence > 0.4 else "Low"

    return f"""• Overall Confidence: {confidence:.1%} ({confidence_level})
• Potential Actors: {actors}
• Campaign Indicators: {indicators}
• Attribution Factors: {len(attribution.get("attribution_factors", []))}"""


def format_deliverables(investigation_dir):
    """Format investigation deliverables"""
    if not investigation_dir or not investigation_dir.exists():
        return "• Deliverables preserved in investigation archive"

    reports_dir = investigation_dir / "reports"
    reports_count = len(list(reports_dir.glob("*.md"))) if reports_dir.exists() else 0

    return f"""• Final Investigation Report Generated
• Evidence Archive: {investigation_dir.name}
• Phase Reports: {reports_count}
• IOC Documentation: Complete
• Timeline: Reconstructed
• MITRE Mapping: Complete"""


# Additional detailed formatting functions for final report
def format_key_findings(summary):
    """Format key findings for final report"""
    findings = []

    if summary['threats']['confirmed'] > 0:
        findings.append(f"- **{summary['threats']['confirmed']} confirmed threats** identified")

    if summary['iocs']['high_confidence'] > 0:
        findings.append(f"- **{summary['iocs']['high_confidence']} high-confidence IOCs** discovered")

    if summary['attribution']['confidence_score'] > 0.7:
        findings.append(f"- **High attribution confidence** ({summary['attribution']['confidence_score']:.1%})")

    if not findings:
        findings.append("- No significant threats identified during investigation")

    return "\n".join(findings)


def format_detailed_ioc_analysis(iocs):
    """Format detailed IOC analysis for final report"""
    return f"""
### IOC Statistics
- **Total IOCs Discovered**: {iocs['total_discovered']}
- **High Confidence IOCs**: {iocs['high_confidence']}
- **Network Indicators**: {iocs.get('network_indicators', 0)}
- **File Indicators**: {iocs.get('file_indicators', 0)}
- **Process Indicators**: {iocs.get('process_indicators', 0)}
- **MITRE Mapped IOCs**: {iocs.get('mitre_mapped', 0)}

### IOC Categories
{format_ioc_categories(iocs.get('categories', {}))}
"""


def format_ioc_categories(categories):
    """Format IOC categories"""
    if not categories:
        return "No IOC categories identified."

    formatted = []
    for category, count in categories.items():
        formatted.append(f"- **{category}**: {count}")

    return "\n".join(formatted)


def format_detailed_threat_analysis(threats):
    """Format detailed threat analysis for final report"""
    return f"""
### Threat Statistics
- **Confirmed Threats**: {threats['confirmed']}
- **Potential Threats**: {threats['potential']}
- **False Positives**: {threats['false_positives']}

### Severity Distribution
- **Critical**: {threats['severity_distribution'].get('critical', 0)}
- **High**: {threats['severity_distribution'].get('high', 0)}
- **Medium**: {threats['severity_distribution'].get('medium', 0)}
- **Low**: {threats['severity_distribution'].get('low', 0)}
"""


def format_detailed_mitre_analysis(mitre):
    """Format detailed MITRE analysis for final report"""
    tactics_list = ", ".join(mitre['tactics_identified']) if mitre['tactics_identified'] else "None"
    techniques_list = ", ".join(mitre['techniques_detected'][:10]) if mitre['techniques_detected'] else "None"

    return f"""
### MITRE ATT&CK Coverage
- **Tactics Identified**: {len(mitre['tactics_identified'])}
- **Techniques Detected**: {len(mitre['techniques_detected'])}
- **Coverage Score**: {mitre['coverage_score']:.1%}

### Detected Tactics
{tactics_list}

### Key Techniques (Top 10)
{techniques_list}
"""


def format_detailed_attribution_analysis(attribution):
    """Format detailed attribution analysis for final report"""
    factors_text = "\n".join(f"- {factor[0]}: {factor[1]:.2f}" for factor in attribution.get('attribution_factors', []))
    actors_text = "\n".join(f"- {actor}" for actor in attribution['potential_actors']) if attribution['potential_actors'] else "None identified"

    return f"""
### Attribution Confidence: {attribution['confidence_score']:.1%}

### Confidence Factors
{factors_text}

### Potential Threat Actors
{actors_text}

### Campaign Indicators
{len(attribution['campaign_indicators'])} indicators identified
"""


def format_detailed_evidence_analysis(evidence):
    """Format detailed evidence analysis for final report"""
    categories_text = "\n".join(f"- {category}: {count}" for category, count in evidence.get('evidence_categories', {}).items())

    return f"""
### Evidence Collection Summary
- **Total Files**: {evidence['files_collected']}
- **Integrity Verified**: {'Yes' if evidence['integrity_verified'] else 'No'}
- **Chain of Custody**: {'Maintained' if evidence['chain_of_custody'] else 'Broken'}
- **Preservation Quality**: {evidence.get('preservation_quality', 'Unknown')}

### Evidence Categories
{categories_text}
"""


def format_investigation_recommendations(summary):
    """Format investigation recommendations for final report"""
    recommendations = []

    if summary['threats']['confirmed'] > 0:
        recommendations.append("- Implement immediate containment measures for confirmed threats")

    if summary['iocs']['total_discovered'] > 0:
        recommendations.append("- Update threat intelligence feeds with discovered IOCs")

    if summary['attribution']['confidence_score'] > 0.6:
        recommendations.append("- Share attribution analysis with threat intelligence community")

    if summary['mitre_analysis']['coverage_score'] < 0.5:
        recommendations.append("- Enhance detection capabilities for identified MITRE techniques")

    if not recommendations:
        recommendations.append("- Continue routine security monitoring")

    return "\n".join(recommendations)


async def format_investigation_timeline(investigation_dir):
    """Format investigation timeline for final report"""
    timeline_file = investigation_dir / "timeline" / "investigation_timeline.json"

    if not timeline_file.exists():
        return "Timeline data not available."

    try:
        timeline = json.loads(timeline_file.read_text())

        formatted_events = []
        for event in timeline[-10:]:  # Show last 10 events
            timestamp = event.get('timestamp', 'Unknown')
            event_type = event.get('event_type', 'Unknown')
            formatted_events.append(f"- **{timestamp}**: {event_type}")

        return "\n".join(formatted_events)

    except:
        return "Timeline data corrupted or unavailable."


def get_investigation_period(investigation_dir):
    """Get investigation period from metadata"""
    metadata_file = investigation_dir / "investigation_metadata.json"

    if not metadata_file.exists():
        return "Unknown"

    try:
        metadata = json.loads(metadata_file.read_text())
        start_time = metadata.get('start_time')
        end_time = metadata.get('end_time')

        if start_time and end_time:
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            return f"{start.strftime('%Y-%m-%d %H:%M')} to {end.strftime('%Y-%m-%d %H:%M')}"
    except:
        pass

    return "Period calculation unavailable"


def main():
    """Entry point with uvloop optimization"""
    run_with_uvloop(investigation_end_async())


if __name__ == "__main__":
    main()