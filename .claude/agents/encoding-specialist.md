# Live Linux Forensics: Comprehensive Methodology & Tool Inventory
**with MCP + Claude Integration**

**Version**: 2026-04-10 (MCP-Enhanced + Encoding Specialist Agent)
**Scope**: Volatile (live) data collection **and AI-assisted analysis** on running Linux systems
**MCP Status**: Fully compatible with **Claude Desktop / Claude Code** via Model Context Protocol (MCP)
**Sources synthesized**:
- GitHub repos (UAC, Live-Forensicator, LinuxCatScale, Linux Expl0rer, POFR, Volatility3-MCP)
- Awesome Forensics lists & DFIR community resources
- Live distros (CAINE, Tsurugi, Kali Forensic Mode, DEFT, SIFT)
- Package repositories (CERT Forensics Tools, Debian `forensics-all`, SIFT PPA)
- LiME & AVML official repositories
- **Volatility3 MCP Server** (Kirandawadi/volatility3-mcp)

---

## MCP + Claude Quick-Start

This document is now **MCP-ready**. You can connect it directly to **Claude** (Claude Desktop or Claude Code) so Claude can:
- Read the entire methodology in real time
- Run live-forensics commands
- Analyze LiME/AVML dumps with Volatility 3
- Generate automated reports

### How to Register this Document as an MCP Knowledge Source

```bash
# 1. Save this file as live-linux-forensics.md in your Claude project

# 2. Register the forensics document
claude mcp add live-linux-forensics \
  --transport file \
  --path "$(pwd)/live-linux-forensics.md" \
  --scope project

# 3. (Recommended) Also add the Volatility3 MCP Server for automated memory analysis
claude mcp add volatility3 \
  --command "python3" \
  --args "/absolute/path/to/volatility3-mcp/bridge_mcp_volatility.py"

Once registered, tell Claude:
“Using the live-linux-forensics MCP, perform a full Phase 1 memory acquisition on the target and analyze it with Volatility 3.”
Claude will now have persistent, context-aware access to the complete Linux forensics workflow.

1. Live Forensics Methodology (Order of Volatility)
Live forensics must preserve evidence integrity while minimizing system footprint. All major collectors (UAC, Live-Forensicator, LinuxCatScale) follow this sequence automatically or via modular profiles.
Phase 0: Preparation & Documentation (Baseline)

Record investigator details, case number, date/time, system hostname, kernel version (uname -a), and current UTC offset.
Use known-good binaries from external read-only media (USB boot or write-blocked drive).
Note any anti-forensics indicators (SELinux/AppArmor status, loaded kernel modules).
Disable swap if authorized and document the action.

Phase 1: Volatile Memory Acquisition (Highest Priority)
Capture full RAM before any other activity. Two primary tools:
1.1 LiME (Linux Memory Extractor)
Latest Version: 1.12.0
Repository: https://github.com/504ensicsLabs/LiME
Type: Loadable Kernel Module (LKM)
Build & Run: