# MalwareHunter APT Investigation Commands

This directory contains specialized cybersecurity investigation commands designed for the MalwareHunter project, compatible with any Linux distribution.

## 🔧 Dynamic System Detection

The MalwareHunter suite **automatically detects and adapts** to your system configuration:

- **Operating System**: Auto-detects Linux distribution (Ubuntu, Arch, Fedora, openSUSE, etc.)
- **Desktop Environment**: Identifies GNOME, KDE, COSMIC, XFCE, etc.
- **Browsers**: Detects installed browsers (Brave, Chrome, Firefox, Chromium)
- **GPU Hardware**: Discovers NVIDIA, AMD, Intel graphics devices
- **Package Manager**: Identifies pacman, apt, dnf, zypper, etc.
- **Security Features**: Checks Secure Boot, IOMMU, ptrace settings
- **Available Tools**: Verifies presence of forensic utilities

## 📁 Configurable Environment

The suite respects user preferences and system layout:

```bash
# Set custom base directory (default: ~/MalwareHunter)
export MALWAREHUNTER_BASE_DIR=/opt/security/investigations

# Session directories are created automatically:
# $MALWAREHUNTER_BASE_DIR/sessions/YYYYMMDD_HHMMSS/
```

## 🔧 Available Commands

### 1. `apt-hunt` - Advanced Persistent Threat Detection
**Primary APT investigation tool targeting known threat vectors with dynamic system adaptation**

```bash
./apt-hunt [--quick|--deep] [--target process|network|browser|gpu|logs|all]
```

**Capabilities:**
- 🔍 **Dynamic GPU Analysis** - Detects screenshot exfiltration via auto-discovered framebuffer and GPU devices
- 🌐 **Multi-Browser Detection** - Identifies compromise across all installed browsers (Brave, Chrome, Firefox, etc.)
- 🔗 **Network Anomaly Detection** - Hunts ARP spoofing, NAT hiding, unusual connections
- 📋 **Log Tampering Detection** - Verifies journal integrity and detects log manipulation
- ⚡ **Process Injection Detection** - Identifies suspicious memory access and ptrace usage
- 🏷️ **Smart Filtering** - Uses system-specific legitimate service whitelist

**Auto-Adaptation:**
- Detects available GPU devices (/dev/fb*, /dev/nvidia*, /dev/dri/*)
- Adapts browser analysis to installed browsers
- Customizes legitimate process whitelist based on detected desktop environment
- Uses available network analysis tools (ss, netstat, ip)

**Example:**
```bash
./apt-hunt --target all          # Full system APT scan (adapts to your system)
./apt-hunt --target gpu          # Focus on GPU/screenshot capabilities
./apt-hunt --target browser      # Check all detected browsers
```

---

### 2. `rootkit-scan` - Advanced Rootkit Detection
**Deep system integrity and rootkit detection scanner**

```bash
./rootkit-scan [--normal|--deep] [--target system|kernel|files|network|all]
```

**Capabilities:**
- 👻 **Hidden Process Detection** - Uses `unhide` and `/proc` discrepancy analysis
- 🔧 **Kernel Module Analysis** - Detects unsigned, suspicious, or injected kernel modules
- 🛡️ **System Integrity Checks** - Validates critical binaries with `rkhunter` integration
- 🔗 **Network Backdoor Detection** - Hunts suspicious listening ports and connections
- ⏰ **Timestamp Anomaly Detection** - Identifies tampered file timestamps

**Example:**
```bash
./rootkit-scan --deep           # Comprehensive rootkit scan
./rootkit-scan --target kernel  # Focus on kernel modules
```

---

### 3. `memory-dump` - Memory Forensics Analysis
**Advanced process memory analysis and injection detection**

```bash
./memory-dump [--analyze] [--target process|browser|system|all] [--pid PID]
```

**Capabilities:**
- 💉 **Process Injection Detection** - Analyzes memory maps for suspicious regions
- 🧠 **Memory Dump Collection** - Uses `gcore` for forensic memory acquisition
- 🔍 **Browser Memory Analysis** - Specialized Brave browser memory investigation
- ⚠️ **System Memory Integrity** - Detects kernel memory corruption and anomalies
- 🔎 **String Analysis** - Extracts and analyzes suspicious patterns from memory

**Example:**
```bash
./memory-dump --target browser  # Analyze browser memory
./memory-dump --pid 1234        # Dump specific process
```

---

### 4. `net-hunt` - Network Traffic Analysis
**Advanced network forensics and C2 detection**

```bash
./net-hunt [--capture] [--analyze] [--duration SECONDS]
```

**Capabilities:**
- 🔀 **ARP Spoofing Detection** - Identifies MAC/IP conflicts and spoofing attempts
- 🌐 **Active Connection Analysis** - Hunts suspicious processes and ports
- 🛣️ **Routing Table Analysis** - Detects malicious route modifications
- 🛡️ **Iptables Rule Analysis** - Checks for traffic redirection and hiding
- 📦 **PCAP Analysis** - Traffic capture and suspicious pattern detection with `tshark`

**Example:**
```bash
./net-hunt --capture --duration 300  # Capture 5 minutes of traffic
./net-hunt                           # Quick network analysis
```

---

### 5. `browser-hunt` - Browser Compromise Investigation
**Adaptive browser forensics for any installed browser**

```bash
./browser-hunt [--deep] [--browser brave|chrome|firefox|all] [--cookies] [--extensions]
```

**Capabilities:**
- 🍪 **Multi-Browser Cookie Analysis** - Analyzes cookie databases for all detected browsers
- 🔌 **Extension Malware Detection** - Scans browser extensions across different browsers
- 📊 **Browser History Forensics** - Detects suspicious URLs and downloads
- ⚙️ **Process Memory Analysis** - Identifies browser injection via LD_PRELOAD
- 🔧 **Configuration Analysis** - Detects malicious browser setting modifications

**Auto-Adaptation:**
- Automatically detects installed browsers (Brave, Chrome, Firefox, Chromium)
- Adapts file paths based on system and browser version
- Handles different browser database formats (SQLite, JSON, etc.)
- Customizes analysis based on browser-specific features

**Example:**
```bash
./browser-hunt --browser all --deep     # Deep analysis of all detected browsers
./browser-hunt --extensions             # Focus on extension analysis
```

---

### 6. `malware-hunter` - Main Launcher
**Unified launcher for all investigation commands**

```bash
./malware-hunter [command] [options]
```

**Example:**
```bash
./malware-hunter apt-hunt --target all
./malware-hunter net-hunt --capture --duration 120
```

## 📁 Session Output Structure

All commands create structured session directories that adapt to your system configuration:
```
${MALWAREHUNTER_BASE_DIR:-~/MalwareHunter}/sessions/YYYYMMDD_HHMMSS/
├── findings.md                 # Human-readable findings
├── system_config.json          # Auto-detected system configuration
├── *_findings.json             # Machine-readable findings
├── artifacts/                  # Evidence and dumps
│   ├── network/               # Network captures and logs
│   ├── memory/                # Memory dumps
│   ├── browser/               # Browser artifacts
│   ├── processes/             # Process information
│   └── packages/              # Package manager data
└── raw_dumps/                 # Raw forensic data
```

The `system_config.json` file contains:
```json
{
  "os": "Ubuntu 22.04",
  "desktop": {"environment": "GNOME", "display_server": "Wayland"},
  "browsers": {"firefox": {"installed": true, "config_dir": "..."}},
  "gpu": {"nvidia_devices": ["/dev/nvidia0"], "framebuffer_devices": []},
  "tools": {"network_analysis": {"tcpdump": true, "tshark": false}},
  "security": {"secure_boot": "enabled", "ptrace_scope": 1}
}
```

## 🎯 Universal APT Threat Coverage

The commands adapt their detection logic based on your system:

| **Threat Category** | **Detection Command** | **System Adaptation** |
|---------------------|----------------------|------------------------|
| Desktop screenshot via C2 | `apt-hunt --target gpu` | Auto-detects GPU devices and framebuffers |
| Browser session hijacking | `browser-hunt --cookies` | Works with any installed browser |
| DOM manipulation | `browser-hunt --deep` | Adapts to browser-specific storage formats |
| Network MITM/spoofing | `net-hunt` | Uses available network tools |
| Process injection | `memory-dump --target process` | Adapts to system architecture |
| Log tampering | `apt-hunt --target logs` | Works with systemd or syslog |
| Kernel rootkits | `rootkit-scan --target kernel` | Adapts to kernel version and modules |

## 🚀 Quick Investigation Workflow

**Rapid APT Assessment:**
```bash
# 1. Quick system-wide APT scan
./apt-hunt

# 2. Check for rootkits
./rootkit-scan

# 3. Browser compromise check
./browser-hunt --cookies

# 4. Network anomaly scan
./net-hunt
```

**Deep Investigation:**
```bash
# 1. Comprehensive APT analysis
./apt-hunt --deep --target all

# 2. Memory forensics
./memory-dump --target all

# 3. Network traffic capture
./net-hunt --capture --duration 300

# 4. Deep browser analysis
./browser-hunt --deep --browser all
```

## 🔐 Security Notes

- All commands require appropriate sudo privileges for system-level analysis
- Commands are **non-destructive** and **read-only** by design
- Evidence is preserved in structured session directories
- Commands integrate with existing MalwareHunter infrastructure

## 📋 Dependencies & Compatibility

The suite automatically checks tool availability and adapts accordingly:

### Core Requirements (always needed)
- Python 3.6+ with standard library
- Basic Linux utilities: `ps`, `find`, `stat`

### Optional Tools (auto-detected and used if available)
- **Rootkit Detection**: `rkhunter`, `unhide`, `lynis`
- **Network Analysis**: `tcpdump`, `tshark`, `nmap`, `ss`, `ip`
- **Memory Analysis**: `gcore`, `strings`, `hexdump`
- **System Analysis**: `lsof`, `strace`, `ltrace`
- **Package Analysis**: Distribution-specific package managers

### Supported Linux Distributions
- ✅ **Arch-based**: Arch Linux, Manjaro, Garuda, EndeavourOS
- ✅ **Debian-based**: Ubuntu, Debian, Mint, Pop!_OS
- ✅ **Red Hat-based**: Fedora, RHEL, CentOS, Rocky Linux
- ✅ **SUSE-based**: openSUSE Leap/Tumbleweed, SLES
- ✅ **Gentoo**: Portage-based systems
- ✅ **Others**: Any modern Linux with standard tools

### Supported Browsers
- ✅ **Chromium-based**: Chrome, Brave, Chromium, Edge
- ✅ **Firefox-based**: Firefox, Waterfox, LibreWolf
- ✅ **Auto-detection**: Finds browser config directories automatically

---

*Part of the MalwareHunter APT Investigation Project - Universal Linux Compatibility*