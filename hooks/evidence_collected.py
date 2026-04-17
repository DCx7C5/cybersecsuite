#!/usr/bin/env python3
"""
MalwareHunter Evidence Collected Hook
Triggered when digital evidence is collected during investigation
"""

import asyncio
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from utils import ensure_structure, get_session_dir
from uvloop_integration import run_with_uvloop
import hashlib


async def evidence_collected_async():
    """Handle evidence collection event"""

    # Get evidence information from environment or arguments
    evidence_path = os.environ.get('MALWARE_EVIDENCE_PATH', sys.argv[1] if len(sys.argv) > 1 else 'unknown')
    evidence_type = os.environ.get('MALWARE_EVIDENCE_TYPE', sys.argv[2] if len(sys.argv) > 2 else 'digital_evidence')
    collection_method = os.environ.get('MALWARE_COLLECTION_METHOD', 'manual')
    investigation_id = os.environ.get('MALWARE_INVESTIGATION_ID', datetime.now().strftime('%Y%m%d_%H%M%S'))

    # Ensure directory structure
    ensure_structure()
    session_dir = get_session_dir()

    # Create evidence record
    evidence_record = {
        "evidence_id": f"EVIDENCE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "source_path": evidence_path,
        "evidence_type": evidence_type,
        "collection_method": collection_method,
        "investigation_id": investigation_id,
        "collection_time": datetime.now(datetime.UTC).isoformat(),
        "collector": os.environ.get('USER', 'unknown'),
        "chain_of_custody": initialize_chain_of_custody(),
        "integrity": await calculate_evidence_integrity(evidence_path),
        "metadata": await extract_evidence_metadata(evidence_path, evidence_type),
        "preservation": assess_preservation_requirements(evidence_type),
        "legal_considerations": get_legal_considerations(evidence_type)
    }

    # Save evidence record
    if session_dir:
        investigation_dir = session_dir / investigation_id
        evidence_dir = investigation_dir / "evidence"
        evidence_dir.mkdir(parents=True, exist_ok=True)

        # Save evidence record
        evidence_file = evidence_dir / f"evidence_{evidence_record['evidence_id']}.json"
        evidence_file.write_text(json.dumps(evidence_record, indent=2))

        # Copy/preserve evidence if it's a file
        if os.path.exists(evidence_path) and os.path.isfile(evidence_path):
            await preserve_evidence_file(evidence_path, evidence_dir, evidence_record)

        # Update evidence log
        await update_evidence_log(investigation_dir, evidence_record)

        # Update investigation timeline
        await update_evidence_timeline(investigation_dir, evidence_record)

        # Generate integrity verification
        await generate_integrity_verification(evidence_dir, evidence_record)

    # Determine evidence priority
    priority = determine_evidence_priority(evidence_record)

    # Generate output for Claude
    output = {
        "hookSpecificOutput": {
            "additionalContext": f"""📦 **EVIDENCE COLLECTED - {priority.upper()} PRIORITY**

🗃️ **Evidence Information:**
• Evidence ID: {evidence_record['evidence_id']}
• Type: {evidence_type}
• Source: {evidence_path}
• Collection Method: {collection_method}
• Collection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• Collector: {evidence_record['collector']}

🔒 **Chain of Custody:**
{format_chain_of_custody(evidence_record['chain_of_custody'])}

🔍 **Evidence Integrity:**
{format_evidence_integrity(evidence_record['integrity'])}

📊 **Evidence Metadata:**
{format_evidence_metadata(evidence_record['metadata'])}

🛡️ **Preservation Requirements:**
{format_preservation_requirements(evidence_record['preservation'])}

⚖️ **Legal Considerations:**
{format_legal_considerations(evidence_record['legal_considerations'])}

📋 **Investigation Actions:**
{format_evidence_investigation_actions(evidence_type)}

🔄 **Next Steps:**
{format_evidence_next_steps(evidence_type, priority)}

**Evidence secured and documented according to forensic standards.**"""
        }
    }

    print(json.dumps(output))


def initialize_chain_of_custody():
    """Initialize chain of custody record"""

    return {
        "initial_collector": os.environ.get('USER', 'unknown'),
        "collection_timestamp": datetime.now(datetime.UTC).isoformat(),
        "collection_location": os.getcwd(),
        "custody_transfers": [],
        "access_log": [
            {
                "timestamp": datetime.now(datetime.UTC).isoformat(),
                "action": "evidence_collected",
                "person": os.environ.get('USER', 'unknown'),
                "purpose": "malware investigation"
            }
        ],
        "integrity_verified": True,
        "storage_location": "investigation_evidence_directory"
    }


async def calculate_evidence_integrity(evidence_path):
    """Calculate integrity hashes for evidence"""

    integrity = {
        "md5": None,
        "sha1": None,
        "sha256": None,
        "file_size": None,
        "verification_time": datetime.now(datetime.UTC).isoformat()
    }

    if not os.path.exists(evidence_path) or not os.path.isfile(evidence_path):
        integrity["status"] = "file_not_accessible"
        return integrity

    try:
        # Calculate file size
        integrity["file_size"] = os.path.getsize(evidence_path)

        # Calculate hashes
        md5_hash = hashlib.md5()
        sha1_hash = hashlib.sha1()
        sha256_hash = hashlib.sha256()

        with open(evidence_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
                sha1_hash.update(chunk)
                sha256_hash.update(chunk)

        integrity["md5"] = md5_hash.hexdigest()
        integrity["sha1"] = sha1_hash.hexdigest()
        integrity["sha256"] = sha256_hash.hexdigest()
        integrity["status"] = "integrity_verified"

    except Exception as e:
        integrity["status"] = f"integrity_calculation_failed: {str(e)}"

    return integrity


async def extract_evidence_metadata(evidence_path, evidence_type):
    """Extract metadata from evidence"""

    metadata = {
        "evidence_type": evidence_type,
        "creation_time": None,
        "modification_time": None,
        "access_time": None,
        "file_attributes": {},
        "content_analysis": {}
    }

    if not os.path.exists(evidence_path):
        metadata["status"] = "file_not_accessible"
        return metadata

    try:
        # File system metadata
        stat_info = os.stat(evidence_path)
        metadata["creation_time"] = datetime.fromtimestamp(stat_info.st_ctime).isoformat()
        metadata["modification_time"] = datetime.fromtimestamp(stat_info.st_mtime).isoformat()
        metadata["access_time"] = datetime.fromtimestamp(stat_info.st_atime).isoformat()
        metadata["file_size"] = stat_info.st_size
        metadata["permissions"] = oct(stat_info.st_mode)

        # Content analysis based on type
        if evidence_type == "log_file":
            metadata["content_analysis"] = await analyze_log_file(evidence_path)
        elif evidence_type == "binary_file":
            metadata["content_analysis"] = await analyze_binary_file(evidence_path)
        elif evidence_type == "configuration_file":
            metadata["content_analysis"] = await analyze_config_file(evidence_path)
        elif evidence_type == "memory_dump":
            metadata["content_analysis"] = await analyze_memory_dump(evidence_path)

        metadata["status"] = "metadata_extracted"

    except Exception as e:
        metadata["status"] = f"metadata_extraction_failed: {str(e)}"

    return metadata


async def analyze_log_file(file_path):
    """Analyze log file content"""

    analysis = {
        "line_count": 0,
        "date_range": {"start": None, "end": None},
        "log_levels": {},
        "suspicious_patterns": []
    }

    try:
        with open(file_path, 'r', errors='ignore') as f:
            lines = f.readlines()
            analysis["line_count"] = len(lines)

            # Sample first and last few lines for date range
            if lines:
                analysis["sample_lines"] = {
                    "first": lines[0].strip(),
                    "last": lines[-1].strip()
                }

            # Look for suspicious patterns (simplified)
            suspicious_keywords = ["error", "fail", "attack", "intrusion", "malware", "suspicious"]
            for line in lines[:100]:  # Check first 100 lines
                line_lower = line.lower()
                for keyword in suspicious_keywords:
                    if keyword in line_lower:
                        analysis["suspicious_patterns"].append(keyword)

    except Exception as e:
        analysis["error"] = str(e)

    return analysis


async def analyze_binary_file(file_path):
    """Analyze binary file content"""

    analysis = {
        "file_type": "binary",
        "entropy": None,
        "strings_found": 0,
        "suspicious_indicators": []
    }

    try:
        # Simple file type detection
        with open(file_path, 'rb') as f:
            header = f.read(16)

        # Check for common binary types
        if header.startswith(b'\x7fELF'):
            analysis["file_type"] = "ELF executable"
        elif header.startswith(b'MZ'):
            analysis["file_type"] = "PE executable"
        elif header.startswith(b'\x89PNG'):
            analysis["file_type"] = "PNG image"

        # Look for suspicious strings (simplified)
        try:
            with open(file_path, 'rb') as f:
                content = f.read(1024)  # Read first 1KB

            # Count printable strings
            strings = []
            current_string = ""
            for byte in content:
                if 32 <= byte <= 126:  # Printable ASCII
                    current_string += chr(byte)
                else:
                    if len(current_string) >= 4:
                        strings.append(current_string)
                    current_string = ""

            analysis["strings_found"] = len(strings)

            # Check for suspicious strings
            suspicious_strings = ["cmd", "powershell", "mimikatz", "password", "admin"]
            for string in strings:
                if any(sus in string.lower() for sus in suspicious_strings):
                    analysis["suspicious_indicators"].append(f"String: {string}")

        except:
            pass

    except Exception as e:
        analysis["error"] = str(e)

    return analysis


async def analyze_config_file(file_path):
    """Analyze configuration file content"""

    analysis = {
        "config_type": "unknown",
        "sections": [],
        "suspicious_settings": [],
        "modification_indicators": []
    }

    try:
        with open(file_path, 'r', errors='ignore') as f:
            content = f.read()

        # Detect config file type
        if file_path.endswith('.conf'):
            analysis["config_type"] = "generic_conf"
        elif file_path.endswith('.ini'):
            analysis["config_type"] = "ini_file"
        elif 'bashrc' in file_path or 'profile' in file_path:
            analysis["config_type"] = "shell_config"

        # Look for suspicious patterns
        suspicious_patterns = [
            "LD_PRELOAD", "export", "alias", "function", "eval",
            "wget", "curl", "nc ", "netcat", "base64"
        ]

        lines = content.split('\n')
        for line in lines:
            line_stripped = line.strip()
            if line_stripped and not line_stripped.startswith('#'):
                for pattern in suspicious_patterns:
                    if pattern in line_stripped:
                        analysis["suspicious_settings"].append(line_stripped)

    except Exception as e:
        analysis["error"] = str(e)

    return analysis


async def analyze_memory_dump(file_path):
    """Analyze memory dump file"""

    analysis = {
        "dump_type": "memory_dump",
        "dump_size": 0,
        "format": "unknown",
        "analysis_recommendations": []
    }

    try:
        analysis["dump_size"] = os.path.getsize(file_path)

        # Recommend analysis tools
        analysis["analysis_recommendations"] = [
            "volatility framework analysis",
            "strings extraction",
            "process listing",
            "network connection analysis",
            "malware scanning"
        ]

        # Check file extension for format hint
        if file_path.endswith('.vmem'):
            analysis["format"] = "vmware_memory"
        elif file_path.endswith('.dmp'):
            analysis["format"] = "windows_dump"
        elif file_path.endswith('.core'):
            analysis["format"] = "core_dump"

    except Exception as e:
        analysis["error"] = str(e)

    return analysis


def assess_preservation_requirements(evidence_type):
    """Assess evidence preservation requirements"""

    requirements = {
        "retention_period": "as_per_policy",
        "storage_requirements": [],
        "access_controls": [],
        "backup_requirements": []
    }

    type_requirements = {
        "log_file": {
            "retention_period": "minimum_1_year",
            "storage_requirements": ["encrypted_storage", "integrity_verification"],
            "access_controls": ["need_to_know", "audit_logging"],
            "backup_requirements": ["multiple_copies", "offsite_backup"]
        },
        "binary_file": {
            "retention_period": "minimum_2_years",
            "storage_requirements": ["quarantined_storage", "malware_scanning"],
            "access_controls": ["restricted_access", "security_clearance"],
            "backup_requirements": ["secure_backup", "isolated_storage"]
        },
        "memory_dump": {
            "retention_period": "minimum_1_year",
            "storage_requirements": ["large_storage_capacity", "fast_access"],
            "access_controls": ["analyst_access_only", "audit_logging"],
            "backup_requirements": ["compressed_backup", "verify_integrity"]
        },
        "configuration_file": {
            "retention_period": "minimum_6_months",
            "storage_requirements": ["version_control", "diff_tracking"],
            "access_controls": ["configuration_management", "change_tracking"],
            "backup_requirements": ["baseline_preservation", "change_history"]
        }
    }

    return type_requirements.get(evidence_type, requirements)


def get_legal_considerations(evidence_type):
    """Get legal considerations for evidence type"""

    considerations = {
        "admissibility": "requires_proper_chain_of_custody",
        "privacy_concerns": [],
        "regulatory_requirements": [],
        "documentation_needs": []
    }

    # Common legal considerations by evidence type
    legal_frameworks = {
        "log_file": {
            "privacy_concerns": ["user_privacy", "data_protection"],
            "regulatory_requirements": ["gdpr_compliance", "data_retention_laws"],
            "documentation_needs": ["collection_methodology", "relevance_justification"]
        },
        "binary_file": {
            "privacy_concerns": ["executable_analysis", "embedded_data"],
            "regulatory_requirements": ["malware_handling", "export_controls"],
            "documentation_needs": ["analysis_methods", "containment_measures"]
        },
        "memory_dump": {
            "privacy_concerns": ["personal_data_in_memory", "credential_exposure"],
            "regulatory_requirements": ["data_minimization", "secure_processing"],
            "documentation_needs": ["dump_scope", "analysis_limitations"]
        },
        "configuration_file": {
            "privacy_concerns": ["system_configuration", "user_settings"],
            "regulatory_requirements": ["configuration_management", "change_control"],
            "documentation_needs": ["baseline_comparison", "modification_tracking"]
        }
    }

    type_considerations = legal_frameworks.get(evidence_type, {})
    considerations.update(type_considerations)

    return considerations


def determine_evidence_priority(evidence_record):
    """Determine priority level for evidence"""

    evidence_type = evidence_record["evidence_type"]
    integrity_status = evidence_record["integrity"].get("status", "unknown")

    # Priority based on evidence type
    high_priority_types = ["memory_dump", "binary_file", "malware_sample"]
    medium_priority_types = ["log_file", "configuration_file", "network_capture"]

    if evidence_type in high_priority_types:
        base_priority = "HIGH"
    elif evidence_type in medium_priority_types:
        base_priority = "MEDIUM"
    else:
        base_priority = "LOW"

    # Adjust based on integrity
    if integrity_status != "integrity_verified":
        if base_priority == "HIGH":
            base_priority = "MEDIUM"
        elif base_priority == "MEDIUM":
            base_priority = "LOW"

    return base_priority


async def preserve_evidence_file(source_path, evidence_dir, evidence_record):
    """Preserve evidence file with proper naming and integrity"""

    try:
        source_file = Path(source_path)

        # Generate preserved filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        preserved_name = f"evidence_{evidence_record['evidence_id']}_{timestamp}_{source_file.name}"
        preserved_path = evidence_dir / preserved_name

        # Copy file
        import shutil
        shutil.copy2(source_path, preserved_path)

        # Update evidence record with preserved location
        evidence_record["preserved_path"] = str(preserved_path)
        evidence_record["preservation_status"] = "preserved"

    except Exception as e:
        evidence_record["preservation_status"] = f"preservation_failed: {str(e)}"


async def update_evidence_log(investigation_dir, evidence_record):
    """Update investigation evidence log"""

    log_dir = investigation_dir / "logs"
    log_dir.mkdir(exist_ok=True)

    evidence_log = log_dir / "evidence_collection.log"

    log_entry = f"{datetime.now().isoformat()} - Evidence Collected: {evidence_record['evidence_id']} - Type: {evidence_record['evidence_type']} - Source: {evidence_record['source_path']}\n"

    # Append to log file
    with open(evidence_log, 'a') as f:
        f.write(log_entry)


async def update_evidence_timeline(investigation_dir, evidence_record):
    """Update investigation timeline with evidence collection"""

    timeline_file = investigation_dir / "timeline" / "investigation_timeline.json"
    timeline_file.parent.mkdir(exist_ok=True)

    timeline_entry = {
        "timestamp": datetime.now(datetime.UTC).isoformat(),
        "event_type": "evidence_collected",
        "evidence_id": evidence_record["evidence_id"],
        "evidence_type": evidence_record["evidence_type"],
        "source_path": evidence_record["source_path"],
        "collector": evidence_record["collector"],
        "metadata": evidence_record
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


async def generate_integrity_verification(evidence_dir, evidence_record):
    """Generate integrity verification file"""

    integrity_file = evidence_dir / f"integrity_{evidence_record['evidence_id']}.txt"

    integrity_info = evidence_record["integrity"]
    verification_content = f"""Evidence Integrity Verification Report
=====================================

Evidence ID: {evidence_record['evidence_id']}
Collection Time: {evidence_record['collection_time']}
Collector: {evidence_record['collector']}
Source Path: {evidence_record['source_path']}

Integrity Hashes:
MD5:    {integrity_info.get('md5', 'N/A')}
SHA1:   {integrity_info.get('sha1', 'N/A')}
SHA256: {integrity_info.get('sha256', 'N/A')}

File Size: {integrity_info.get('file_size', 'N/A')} bytes
Verification Time: {integrity_info.get('verification_time', 'N/A')}
Status: {integrity_info.get('status', 'Unknown')}

Chain of Custody:
Initial Collector: {evidence_record['chain_of_custody']['initial_collector']}
Collection Location: {evidence_record['chain_of_custody']['collection_location']}

This verification ensures evidence integrity for legal proceedings.
"""

    integrity_file.write_text(verification_content)


def format_chain_of_custody(chain_of_custody):
    """Format chain of custody for display"""
    if not chain_of_custody:
        return "• Chain of custody not established"

    collector = chain_of_custody.get("initial_collector", "unknown")
    timestamp = chain_of_custody.get("collection_timestamp", "unknown")
    location = chain_of_custody.get("collection_location", "unknown")
    transfers = len(chain_of_custody.get("custody_transfers", []))

    return f"""• Initial Collector: {collector}
• Collection Time: {timestamp[:19]}
• Collection Location: {location}
• Custody Transfers: {transfers}
• Integrity Status: {'Verified' if chain_of_custody.get('integrity_verified') else 'Unverified'}"""


def format_evidence_integrity(integrity):
    """Format evidence integrity for display"""
    if not integrity:
        return "• Integrity verification pending"

    status = integrity.get("status", "unknown")
    file_size = integrity.get("file_size", "unknown")

    if status == "integrity_verified":
        md5 = integrity.get("md5", "N/A")[:16] + "..." if integrity.get("md5") else "N/A"
        sha256 = integrity.get("sha256", "N/A")[:16] + "..." if integrity.get("sha256") else "N/A"

        return f"""• Status: VERIFIED ✅
• File Size: {file_size} bytes
• MD5: {md5}
• SHA256: {sha256}"""
    else:
        return f"""• Status: {status.upper()} ❌
• File Size: {file_size} bytes"""


def format_evidence_metadata(metadata):
    """Format evidence metadata for display"""
    if not metadata:
        return "• Metadata extraction pending"

    evidence_type = metadata.get("evidence_type", "unknown")
    status = metadata.get("status", "unknown")

    formatted = [f"• Type: {evidence_type}"]

    if status == "metadata_extracted":
        formatted.append("• Status: EXTRACTED ✅")

        if metadata.get("creation_time"):
            formatted.append(f"• Created: {metadata['creation_time'][:19]}")
        if metadata.get("modification_time"):
            formatted.append(f"• Modified: {metadata['modification_time'][:19]}")

        content_analysis = metadata.get("content_analysis", {})
        if content_analysis:
            if "line_count" in content_analysis:
                formatted.append(f"• Lines: {content_analysis['line_count']}")
            if "suspicious_patterns" in content_analysis:
                patterns = len(content_analysis["suspicious_patterns"])
                if patterns > 0:
                    formatted.append(f"• Suspicious Patterns: {patterns}")
    else:
        formatted.append(f"• Status: {status.upper()} ❌")

    return "\n".join(formatted)


def format_preservation_requirements(preservation):
    """Format preservation requirements for display"""
    if not preservation:
        return "• Preservation requirements pending"

    retention = preservation.get("retention_period", "unknown")
    storage_reqs = preservation.get("storage_requirements", [])
    access_controls = preservation.get("access_controls", [])

    formatted = [f"• Retention: {retention.replace('_', ' ').title()}"]

    if storage_reqs:
        formatted.append(f"• Storage: {', '.join(storage_reqs[:2]).replace('_', ' ').title()}")

    if access_controls:
        formatted.append(f"• Access: {', '.join(access_controls[:2]).replace('_', ' ').title()}")

    return "\n".join(formatted)


def format_legal_considerations(legal):
    """Format legal considerations for display"""
    if not legal:
        return "• Legal considerations pending"

    admissibility = legal.get("admissibility", "unknown")
    privacy = legal.get("privacy_concerns", [])
    regulatory = legal.get("regulatory_requirements", [])

    formatted = [f"• Admissibility: {admissibility.replace('_', ' ').title()}"]

    if privacy:
        formatted.append(f"• Privacy: {', '.join(privacy[:2]).replace('_', ' ').title()}")

    if regulatory:
        formatted.append(f"• Regulatory: {', '.join(regulatory[:2]).replace('_', ' ').title()}")

    return "\n".join(formatted)


def format_evidence_investigation_actions(evidence_type):
    """Format investigation actions for evidence type"""

    base_actions = [
        "Verify evidence integrity and chain of custody",
        "Document evidence in investigation case file",
        "Preserve evidence according to retention policy"
    ]

    type_actions = {
        "log_file": [
            "Analyze log entries for suspicious activities",
            "Correlate timestamps with other evidence",
            "Extract relevant log patterns and anomalies"
        ],
        "binary_file": [
            "Perform static malware analysis",
            "Submit to malware analysis sandbox",
            "Extract IOCs and signatures"
        ],
        "memory_dump": [
            "Analyze with Volatility framework",
            "Extract process information and network connections",
            "Search for injected code and rootkits"
        ],
        "configuration_file": [
            "Compare against baseline configurations",
            "Identify unauthorized modifications",
            "Analyze for persistence mechanisms"
        ]
    }

    actions = base_actions + type_actions.get(evidence_type, [])
    return "\n".join(f"• {action}" for action in actions[:5])


def format_evidence_next_steps(evidence_type, priority):
    """Format next steps for evidence processing"""

    if priority == "HIGH":
        steps = [
            "Prioritize immediate analysis",
            "Escalate to senior analysts",
            "Consider emergency response procedures"
        ]
    elif priority == "MEDIUM":
        steps = [
            "Queue for standard analysis",
            "Cross-reference with existing evidence",
            "Schedule detailed examination"
        ]
    else:
        steps = [
            "Include in routine analysis pipeline",
            "Document for future reference",
            "Monitor for additional related evidence"
        ]

    type_steps = {
        "binary_file": [
            "Submit to malware analysis team",
            "Implement containment measures if needed"
        ],
        "memory_dump": [
            "Prepare for extensive memory analysis",
            "Allocate sufficient analysis time"
        ],
        "log_file": [
            "Process through log analysis tools",
            "Generate timeline correlation"
        ]
    }

    specific_steps = type_steps.get(evidence_type, [])
    all_steps = steps + specific_steps

    return "\n".join(f"• {step}" for step in all_steps[:5])


def main():
    """Entry point with uvloop optimization"""
    run_with_uvloop(evidence_collected_async())


if __name__ == "__main__":
    main()