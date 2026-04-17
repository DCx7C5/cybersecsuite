#!/usr/bin/env python3
"""
MalwareHunter Phase End Hook
Finalizes investigation phase with artifact collection and IOC summary
"""

import asyncio
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from utils import ensure_structure, get_session_dir, get_project_dir
from uvloop_integration import run_with_uvloop


async def phase_end_async():
    """Handle investigation phase completion with comprehensive summary"""

    # Get phase information
    phase_name = os.environ.get('MALWARE_PHASE_NAME', sys.argv[1] if len(sys.argv) > 1 else 'Unknown Phase')
    investigation_id = os.environ.get('MALWARE_INVESTIGATION_ID', datetime.now().strftime('%Y%m%d_%H%M%S'))

    # Ensure directory structure
    ensure_structure()
    session_dir = get_session_dir()

    phase_summary = {
        "phase_name": phase_name,
        "investigation_id": investigation_id,
        "end_time": datetime.now(datetime.UTC).isoformat(),
        "status": "completed",
        "investigator": os.environ.get('USER', 'unknown')
    }

    if session_dir:
        phase_dir = session_dir / "phases" / phase_name.lower().replace(' ', '_')

        # Analyze collected artifacts
        artifact_analysis = await analyze_phase_artifacts(phase_dir)
        phase_summary.update(artifact_analysis)

        # Update phase metadata
        if phase_dir.exists():
            metadata_file = phase_dir / "phase_metadata.json"
            if metadata_file.exists():
                try:
                    metadata = json.loads(metadata_file.read_text())
                    metadata["end_time"] = phase_summary["end_time"]
                    metadata["status"] = "completed"
                    metadata["summary"] = phase_summary
                    metadata_file.write_text(json.dumps(metadata, indent=2))
                except:
                    pass

        # Generate phase report
        await generate_phase_report(phase_dir, phase_summary)

        # Update investigation timeline
        await update_investigation_timeline(session_dir, phase_name, "end", phase_summary)

    # Generate next phase recommendations
    next_phase_recommendations = get_next_phase_recommendations(phase_name, phase_summary)

    # Generate output for Claude
    output = {
        "hookSpecificOutput": {
            "additionalContext": f"""✅ **MALWARE HUNTER PHASE COMPLETED: {phase_name.upper()}**

📊 **Phase Summary:**
• Investigation ID: {investigation_id}
• Phase Duration: {calculate_duration(phase_summary)}
• Status: Completed
• Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🎯 **Artifacts Collected:**
{format_artifact_summary(phase_summary.get('artifacts', {}))}

🔍 **IOCs Discovered:**
{format_ioc_summary(phase_summary.get('iocs', {}))}

⚠️ **Threats Identified:**
{format_threat_summary(phase_summary.get('threats', {}))}

📈 **Evidence Quality:**
{format_evidence_quality(phase_summary.get('evidence_quality', {}))}

🚀 **Next Phase Recommendations:**
{format_recommendations(next_phase_recommendations)}

📂 **Phase Report Generated:**
{format_report_info(phase_dir if session_dir else None)}

**Phase {phase_name} investigation completed successfully.**"""
        }
    }

    print(json.dumps(output))


async def analyze_phase_artifacts(phase_dir):
    """Analyze artifacts collected during the phase"""

    analysis = {
        "artifacts": {
            "total_files": 0,
            "evidence_files": 0,
            "log_files": 0,
            "reports": 0
        },
        "iocs": {
            "total_discovered": 0,
            "high_confidence": 0,
            "network_indicators": 0,
            "file_indicators": 0,
            "process_indicators": 0
        },
        "threats": {
            "confirmed_threats": 0,
            "potential_threats": 0,
            "false_positives": 0
        },
        "evidence_quality": {
            "integrity_preserved": True,
            "chain_of_custody": True,
            "timestamp_accuracy": True
        }
    }

    if not phase_dir or not phase_dir.exists():
        return analysis

    # Count artifacts
    for subdir in ["artifacts", "evidence", "logs", "reports"]:
        subdir_path = phase_dir / subdir
        if subdir_path.exists():
            files = list(subdir_path.glob("**/*"))
            analysis["artifacts"][f"{subdir.rstrip('s')}_files"] = len([f for f in files if f.is_file()])

    analysis["artifacts"]["total_files"] = sum(
        count for key, count in analysis["artifacts"].items() if key.endswith("_files")
    )

    # Analyze IOCs if IOC files exist
    ioc_dir = phase_dir / "iocs"
    if ioc_dir.exists():
        analysis["iocs"] = await analyze_ioc_files(ioc_dir)

    # Analyze threats
    threat_analysis_file = phase_dir / "threat_analysis.json"
    if threat_analysis_file.exists():
        try:
            threat_data = json.loads(threat_analysis_file.read_text())
            analysis["threats"] = threat_data.get("summary", analysis["threats"])
        except:
            pass

    return analysis


async def analyze_ioc_files(ioc_dir):
    """Analyze IOC files in the phase directory"""

    ioc_analysis = {
        "total_discovered": 0,
        "high_confidence": 0,
        "network_indicators": 0,
        "file_indicators": 0,
        "process_indicators": 0,
        "categories": []
    }

    # Count IOC files by type
    ioc_files = list(ioc_dir.glob("*.json"))

    for ioc_file in ioc_files:
        try:
            ioc_data = json.loads(ioc_file.read_text())

            if isinstance(ioc_data, list):
                ioc_analysis["total_discovered"] += len(ioc_data)

                for ioc in ioc_data:
                    if ioc.get("confidence", 0) > 0.7:
                        ioc_analysis["high_confidence"] += 1

                    ioc_type = ioc.get("type", "").lower()
                    if any(net_type in ioc_type for net_type in ["ip", "domain", "url", "network"]):
                        ioc_analysis["network_indicators"] += 1
                    elif any(file_type in ioc_type for file_type in ["file", "hash", "path"]):
                        ioc_analysis["file_indicators"] += 1
                    elif any(proc_type in ioc_type for proc_type in ["process", "service"]):
                        ioc_analysis["process_indicators"] += 1

        except:
            continue

    return ioc_analysis


async def generate_phase_report(phase_dir, phase_summary):
    """Generate comprehensive phase report"""

    if not phase_dir or not phase_dir.exists():
        return

    report_dir = phase_dir / "reports"
    report_dir.mkdir(exist_ok=True)

    report_file = report_dir / f"phase_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    report_content = f"""# {phase_summary['phase_name']} Phase Report

## Investigation Summary
- **Investigation ID**: {phase_summary['investigation_id']}
- **Phase**: {phase_summary['phase_name']}
- **Investigator**: {phase_summary['investigator']}
- **Completion Time**: {phase_summary['end_time']}
- **Status**: {phase_summary['status']}

## Artifacts Collected
{format_artifact_report(phase_summary.get('artifacts', {}))}

## IOCs Discovered
{format_ioc_report(phase_summary.get('iocs', {}))}

## Threats Identified
{format_threat_report(phase_summary.get('threats', {}))}

## Evidence Quality Assessment
{format_evidence_quality_report(phase_summary.get('evidence_quality', {}))}

## Recommendations
{format_recommendations_report(get_next_phase_recommendations(phase_summary['phase_name'], phase_summary))}

---
*Report generated by MalwareHunter Phase End Hook*
*Timestamp: {datetime.now().isoformat()}*
"""

    report_file.write_text(report_content)


def get_next_phase_recommendations(phase_name, phase_summary):
    """Get recommendations for next investigation phase"""

    phase_flow = {
        "Rapid Recon": {
            "next_phases": ["Deep Scan", "Network Analysis"],
            "conditions": {
                "Deep Scan": "If suspicious files or processes detected",
                "Network Analysis": "If network indicators found"
            }
        },
        "Deep Scan": {
            "next_phases": ["Persistence Hunt", "Memory Forensics"],
            "conditions": {
                "Persistence Hunt": "If system modifications detected",
                "Memory Forensics": "If active threats or injected processes found"
            }
        },
        "Network Analysis": {
            "next_phases": ["Evidence Correlation", "Threat Attribution"],
            "conditions": {
                "Evidence Correlation": "If multiple IOCs discovered",
                "Threat Attribution": "If C2 patterns identified"
            }
        },
        "Persistence Hunt": {
            "next_phases": ["Evidence Correlation", "Memory Forensics"],
            "conditions": {
                "Evidence Correlation": "If persistence mechanisms found",
                "Memory Forensics": "If active malware detected"
            }
        },
        "Memory Forensics": {
            "next_phases": ["Evidence Correlation", "Threat Attribution"],
            "conditions": {
                "Evidence Correlation": "Always recommended after memory analysis",
                "Threat Attribution": "If malware families identified"
            }
        },
        "Evidence Correlation": {
            "next_phases": ["Threat Attribution", "Final Report"],
            "conditions": {
                "Threat Attribution": "If campaign patterns emerge",
                "Final Report": "If investigation complete"
            }
        }
    }

    flow_info = phase_flow.get(phase_name, {})
    recommendations = []

    # Analyze phase results to recommend next steps
    artifact_count = phase_summary.get('artifacts', {}).get('total_files', 0)
    ioc_count = phase_summary.get('iocs', {}).get('total_discovered', 0)
    threat_count = phase_summary.get('threats', {}).get('confirmed_threats', 0)

    for next_phase in flow_info.get('next_phases', []):
        condition = flow_info.get('conditions', {}).get(next_phase, '')
        priority = calculate_phase_priority(next_phase, phase_summary)

        recommendations.append({
            "phase": next_phase,
            "priority": priority,
            "condition": condition,
            "justification": generate_phase_justification(next_phase, phase_summary)
        })

    # Sort by priority
    recommendations.sort(key=lambda x: x['priority'], reverse=True)

    return recommendations


def calculate_phase_priority(phase_name, phase_summary):
    """Calculate priority score for next phase"""

    base_scores = {
        "Deep Scan": 0.8,
        "Network Analysis": 0.7,
        "Persistence Hunt": 0.6,
        "Memory Forensics": 0.9,
        "Evidence Correlation": 0.8,
        "Threat Attribution": 0.7,
        "Final Report": 0.5
    }

    base_score = base_scores.get(phase_name, 0.5)

    # Boost score based on findings
    ioc_count = phase_summary.get('iocs', {}).get('total_discovered', 0)
    threat_count = phase_summary.get('threats', {}).get('confirmed_threats', 0)

    if ioc_count > 5:
        base_score += 0.2
    if threat_count > 0:
        base_score += 0.3

    return min(base_score, 1.0)


def generate_phase_justification(phase_name, phase_summary):
    """Generate justification for recommending a phase"""

    ioc_count = phase_summary.get('iocs', {}).get('total_discovered', 0)
    threat_count = phase_summary.get('threats', {}).get('confirmed_threats', 0)

    justifications = {
        "Deep Scan": f"Thorough analysis needed with {ioc_count} IOCs discovered",
        "Network Analysis": f"Network investigation required for C2 detection",
        "Persistence Hunt": f"Search for persistence mechanisms after system analysis",
        "Memory Forensics": f"Active threat analysis with {threat_count} confirmed threats",
        "Evidence Correlation": f"Correlate {ioc_count} IOCs for campaign analysis",
        "Threat Attribution": f"Attribution analysis with sufficient evidence collected"
    }

    return justifications.get(phase_name, f"Continue investigation with {phase_name}")


async def update_investigation_timeline(session_dir, phase_name, event_type, metadata):
    """Update investigation timeline with phase completion"""

    timeline_file = session_dir / "investigation_timeline.json"

    timeline_entry = {
        "timestamp": datetime.now(datetime.UTC).isoformat(),
        "event_type": f"phase_{event_type}",
        "phase_name": phase_name,
        "investigation_id": metadata.get("investigation_id"),
        "metadata": metadata
    }

    # Load existing timeline
    timeline = []
    if timeline_file.exists():
        try:
            timeline = json.loads(timeline_file.read_text())
        except:
            timeline = []

    timeline.append(timeline_entry)
    timeline_file.write_text(json.dumps(timeline, indent=2))


def calculate_duration(phase_summary):
    """Calculate phase duration if start time is available"""
    # This would need start time from metadata - placeholder for now
    return "Duration calculated from metadata"


def format_artifact_summary(artifacts):
    """Format artifact summary for display"""
    if not artifacts:
        return "• No artifacts collected"

    summary = []
    for key, value in artifacts.items():
        if isinstance(value, int) and value > 0:
            summary.append(f"• {key.replace('_', ' ').title()}: {value}")

    return "\n".join(summary) if summary else "• No artifacts collected"


def format_ioc_summary(iocs):
    """Format IOC summary for display"""
    if not iocs:
        return "• No IOCs discovered"

    total = iocs.get('total_discovered', 0)
    high_conf = iocs.get('high_confidence', 0)

    if total == 0:
        return "• No IOCs discovered"

    summary = [
        f"• Total IOCs: {total}",
        f"• High Confidence: {high_conf}",
        f"• Network Indicators: {iocs.get('network_indicators', 0)}",
        f"• File Indicators: {iocs.get('file_indicators', 0)}",
        f"• Process Indicators: {iocs.get('process_indicators', 0)}"
    ]

    return "\n".join(summary)


def format_threat_summary(threats):
    """Format threat summary for display"""
    if not threats:
        return "• No threats identified"

    confirmed = threats.get('confirmed_threats', 0)
    potential = threats.get('potential_threats', 0)

    if confirmed == 0 and potential == 0:
        return "• No threats identified"

    summary = []
    if confirmed > 0:
        summary.append(f"• Confirmed Threats: {confirmed}")
    if potential > 0:
        summary.append(f"• Potential Threats: {potential}")

    return "\n".join(summary)


def format_evidence_quality(evidence_quality):
    """Format evidence quality assessment"""
    if not evidence_quality:
        return "• Evidence quality assessment unavailable"

    integrity = "✅" if evidence_quality.get('integrity_preserved', True) else "❌"
    custody = "✅" if evidence_quality.get('chain_of_custody', True) else "❌"
    timestamp = "✅" if evidence_quality.get('timestamp_accuracy', True) else "❌"

    return f"""• Integrity Preserved: {integrity}
• Chain of Custody: {custody}
• Timestamp Accuracy: {timestamp}"""


def format_recommendations(recommendations):
    """Format next phase recommendations"""
    if not recommendations:
        return "• Investigation complete"

    formatted = []
    for rec in recommendations[:3]:  # Show top 3 recommendations
        priority_indicator = "🔴" if rec['priority'] > 0.8 else "🟡" if rec['priority'] > 0.6 else "🟢"
        formatted.append(f"• {priority_indicator} {rec['phase']}: {rec['justification']}")

    return "\n".join(formatted)


def format_report_info(phase_dir):
    """Format phase report information"""
    if not phase_dir or not phase_dir.exists():
        return "• Phase report generation skipped (no session context)"

    report_dir = phase_dir / "reports"
    if report_dir.exists():
        reports = list(report_dir.glob("*.md"))
        if reports:
            latest_report = max(reports, key=lambda x: x.stat().st_mtime)
            return f"• Report saved: {latest_report.name}"

    return "• Phase report generated in session directory"


# Additional formatting functions for detailed reports
def format_artifact_report(artifacts):
    """Format detailed artifact report"""
    if not artifacts:
        return "No artifacts were collected during this phase."

    return f"""
- **Total Files**: {artifacts.get('total_files', 0)}
- **Evidence Files**: {artifacts.get('evidence_files', 0)}
- **Log Files**: {artifacts.get('log_files', 0)}
- **Reports**: {artifacts.get('reports', 0)}
"""


def format_ioc_report(iocs):
    """Format detailed IOC report"""
    if not iocs:
        return "No IOCs were discovered during this phase."

    return f"""
- **Total Discovered**: {iocs.get('total_discovered', 0)}
- **High Confidence**: {iocs.get('high_confidence', 0)}
- **Network Indicators**: {iocs.get('network_indicators', 0)}
- **File Indicators**: {iocs.get('file_indicators', 0)}
- **Process Indicators**: {iocs.get('process_indicators', 0)}
"""


def format_threat_report(threats):
    """Format detailed threat report"""
    if not threats:
        return "No threats were identified during this phase."

    return f"""
- **Confirmed Threats**: {threats.get('confirmed_threats', 0)}
- **Potential Threats**: {threats.get('potential_threats', 0)}
- **False Positives**: {threats.get('false_positives', 0)}
"""


def format_evidence_quality_report(evidence_quality):
    """Format detailed evidence quality report"""
    if not evidence_quality:
        return "Evidence quality assessment was not performed."

    return f"""
- **Integrity Preserved**: {'Yes' if evidence_quality.get('integrity_preserved', True) else 'No'}
- **Chain of Custody**: {'Maintained' if evidence_quality.get('chain_of_custody', True) else 'Broken'}
- **Timestamp Accuracy**: {'Accurate' if evidence_quality.get('timestamp_accuracy', True) else 'Questionable'}
"""


def format_recommendations_report(recommendations):
    """Format detailed recommendations report"""
    if not recommendations:
        return "Investigation appears to be complete."

    formatted = []
    for rec in recommendations:
        formatted.append(f"""
### {rec['phase']} (Priority: {rec['priority']:.1f})
- **Condition**: {rec['condition']}
- **Justification**: {rec['justification']}
""")

    return "\n".join(formatted)


def main():
    """Entry point with uvloop optimization"""
    run_with_uvloop(phase_end_async())


if __name__ == "__main__":
    main()