#!/usr/bin/env python3
"""
YARA Rule Tester Hook – MalwareHunter
Comprehensive, non-destructive testing of generated YARA rules against session artefacts.
"""

import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from utils import ensure_structure, get_session_dir
from uvloop_integration import run_with_uvloop


async def yara_rule_tester_async():
    """Test all YARA rules in the current session"""

    session_dir = get_session_dir()
    investigation_id = os.environ.get('MALWARE_INVESTIGATION_ID', datetime.now().strftime('%Y%m%d_%H%M%S'))
    rule_file_pattern = os.environ.get('YARA_RULE_FILE', '*.yar')

    ensure_structure()

    if not session_dir:
        print(json.dumps({
            "status": "error",
            "message": "No active session directory"
        }))
        return

    yara_dir = session_dir / investigation_id / "yara"
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "investigation_id": investigation_id,
        "total_rules": 0,
        "passed": 0,
        "failed": 0,
        "results": []
    }

    if not yara_dir.exists():
        test_results["message"] = "No YARA rules directory found"
        print(json.dumps({"hookSpecificOutput": {"additionalContext": json.dumps(test_results)}}))
        return

    # Find all .yar files
    rule_files = list(yara_dir.glob(rule_file_pattern))
    test_results["total_rules"] = len(rule_files)

    for rule_file in rule_files:
        result = await test_single_rule(rule_file, session_dir, investigation_id)
        test_results["results"].append(result)
        if result["status"] == "passed":
            test_results["passed"] += 1
        else:
            test_results["failed"] += 1

    # Save test report
    report_dir = yara_dir / "test_reports"
    report_dir.mkdir(exist_ok=True)
    report_file = report_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.write_text(json.dumps(test_results, indent=2))

    # Generate human-readable summary
    summary = generate_test_summary(test_results)

    output = {
        "hookSpecificOutput": {
            "additionalContext": f"""🧪 **YARA RULE TESTING COMPLETE**

**Rules Tested:** {test_results['total_rules']}
**Passed:** {test_results['passed']} ✅
**Failed:** {test_results['failed']} ❌

**Test Report Saved:** {report_file.name}

{summary}

**Next Steps:**
• Review any failed rules in the test report
• Deploy high-confidence rules to watchlist
• Share results to shared-memory layer"""
        }
    }

    print(json.dumps(output))


async def test_single_rule(rule_file: Path, session_dir: Path, investigation_id: str):
    """Test a single YARA rule file against session artefacts"""
    result = {
        "rule_file": rule_file.name,
        "status": "passed",
        "matches": 0,
        "errors": [],
        "tested_paths": []
    }

    try:
        # Test against key artefact directories
        test_paths = [
            session_dir / investigation_id / "artefacts",
            session_dir / investigation_id / "raw_dumps",
            session_dir / "iocs.md",
            session_dir / "findings.md"
        ]

        for path in test_paths:
            if path.exists():
                result["tested_paths"].append(str(path))
                cmd = ["yara", "-r", str(rule_file), str(path)]
                try:
                    proc = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await proc.communicate()
                    if proc.returncode == 0 and stdout.strip():
                        result["matches"] += 1
                except Exception as e:
                    result["errors"].append(f"Test failed on {path}: {e}")

    except Exception as e:
        result["status"] = "failed"
        result["errors"].append(str(e))

    if result["errors"]:
        result["status"] = "failed"

    return result


def generate_test_summary(results):
    """Generate human-readable test summary"""
    summary = []
    for r in results["results"]:
        status_emoji = "✅" if r["status"] == "passed" else "❌"
        summary.append(f"• {status_emoji} **{r['rule_file']}** — {r['matches']} matches")

    return "\n".join(summary)


def main():
    run_with_uvloop(yara_rule_tester_async())


if __name__ == "__main__":
    main()