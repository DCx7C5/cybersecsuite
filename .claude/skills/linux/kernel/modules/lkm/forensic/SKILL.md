---
name: kernel-modules-lkm-forensic
description: Advanced Linux Kernel Module development for cybersecurity forensics. Custom LKM creation for rootkit detection, real-time syscall monitoring, kernel-space threat detection, eBPF forensics, and kerneldev-mcp integration.
model: opus
maxTurns: 30
tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - WebSearch
skills:
  - shared-memory
  - threats/mitre-attack-mapper
  - kerneldev
tags:
- kernel
- linux
- lkm
- kerneldev-forensic
mitre_attack:
- T1014
- T1059
- T1547
- T1547.006
nist_csf: []
capec: []
---

# KernelDev Forensic — Advanced Kernel Development for Cybersecurity

**Purpose:**  
Develop custom Linux Kernel Modules (LKMs) for advanced forensic investigation, rootkit detection, real-time syscall monitoring, and kernel-space threat detection. Integrates with existing CyberSec forensic framework and kerneldev-mcp for seamless development workflow.

---

## Core Capabilities

### 🔧 **Forensic LKM Development**
- **Rootkit Detection Modules**: Custom kernel modules for advanced rootkit and malware detection
- **Syscall Monitoring**: Real-time system call interception and logging
- **Memory Forensics**: Kernel-space memory analysis and artifact collection
- **Network Inspection**: Deep packet inspection at kernel level
- **Process Monitoring**: Advanced process tracking and behavior analysis

### 🛡️ **Real-Time Defense Modules**
- **IOC Detection**: Kernel-space indicator monitoring and alerting
- **Anti-Evasion**: Counter-measures against kernel-level evasion techniques
- **Baseline Verification**: Real-time baseline integrity checking
- **Threat Response**: Automated kernel-space threat containment

### 🔍 **Integration with CyberSec Framework**
- **Database Integration**: Seamless integration with Kernel and KernelModule Tortoise models
- **Session Management**: LKM deployment tracking within investigation sessions
- **Artifact Collection**: Automated forensic artifact capture and storage
- **MalwareHunter Elite**: Enhanced capabilities for the elite forensic agent

---

## Development Environment Setup

### Prerequisites
→ **[`scripts/prerequisites.sh`](scripts/prerequisites.sh)**

```bash
bash scripts/prerequisites.sh
```

### KernelDev-MCP Configuration
Ensure `.claude/mcp.json` is properly configured.  
→ **[`config/kerneldev_mcp.json`](config/kerneldev_mcp.json)**

---

## Forensic LKM Templates

### 1. Sysfs Communication Interface
**Purpose**: Clean kernel ↔ userspace communication for forensic tools  
**File**: [`templates/forensic_sysfs_interface.c`](templates/forensic_sysfs_interface.c)
```
Creates /sys/kernel/forensic_mcp/ with:
- message (rw): Command/response interface
- status (ro): Module status and statistics  
- alerts (ro): Real-time threat alerts
- config (rw): Runtime configuration
```

### 2. Syscall Monitor Module
**Purpose**: Real-time syscall interception for APT detection  
**File**: [`templates/syscall_monitor.c`](templates/syscall_monitor.c)
```
Features:
- Selective syscall monitoring (configurable via sysfs)
- Process filtering by PID/PPID/command
- Real-time logging to ring buffer
- Integration with IOC detection
```

### 3. Rootkit Scanner Module  
**Purpose**: Kernel-space rootkit detection and analysis  
*(Template pending — see scenario example below)*
```
Capabilities:
- SSDT/IDT hook detection
- Hidden process detection via task_struct traversal
- Network connection hiding detection
- Kernel code integrity verification
```

### 4. Memory Forensics Collector
**Purpose**: Advanced memory artifact collection  
*(Template pending — see scenario example below)*
```
Features:
- Live memory dumping
- Process memory mapping analysis
- Kernel heap inspection
- Cache poisoning detection
```

---

## Integration with CyberSec Models

### Database Integration
→ **[`examples/deploy_forensic_module.py`](examples/deploy_forensic_module.py)**

```bash
python -c "
import asyncio
from examples.deploy_forensic_module import deploy_forensic_module
asyncio.run(deploy_forensic_module(kernel_id=1, module_name='syscall_monitor'))
"
```

### Session Integration
→ **[`examples/session_modules.py`](examples/session_modules.py)**

```bash
python -c "
import asyncio
from examples.session_modules import create_forensic_session_modules
asyncio.run(create_forensic_session_modules(session_id='abc123'))
"
```

---

## Development Workflow

### 1. Module Creation
→ **[`examples/module_creation.sh`](examples/module_creation.sh)**

```bash
bash examples/module_creation.sh custom_detector
```

### 2. Build and Test
→ **[`examples/build_and_test.sh`](examples/build_and_test.sh)**

```bash
bash examples/build_and_test.sh custom_detector
```

### 3. Integration Testing
→ **[`examples/integration_testing.sh`](examples/integration_testing.sh)**

```bash
bash examples/integration_testing.sh custom_detector
```

---

## Security Considerations

### Module Signing
→ **[`scripts/sign_module.sh`](scripts/sign_module.sh)**

```bash
bash scripts/sign_module.sh module.ko
```

### Safety Measures
- **Test Environment**: Always develop in isolated VM/container
- **Backup Protection**: Automatic kernel backup before module load
- **Failure Recovery**: Safe module removal and system restoration
- **Audit Trail**: Complete deployment and removal logging

---

## Example Forensic Scenarios

### Scenario 1: APT Syscall Analysis
→ **[`examples/scenario_apt_syscall.sh`](examples/scenario_apt_syscall.sh)**

```bash
bash examples/scenario_apt_syscall.sh
```

### Scenario 2: Rootkit Detection Campaign  
→ **[`examples/scenario_rootkit_detection.sh`](examples/scenario_rootkit_detection.sh)**

```bash
bash examples/scenario_rootkit_detection.sh
```

### Scenario 3: Memory Forensics Collection
→ **[`examples/scenario_memory_forensics.sh`](examples/scenario_memory_forensics.sh)**

```bash
bash examples/scenario_memory_forensics.sh /forensic/memory-artifacts
```

---

## MCP Integration Commands

→ **[`examples/mcp_commands.sh`](examples/mcp_commands.sh)**

```bash
SESSION_ID=<your-session-id> bash examples/mcp_commands.sh
```

---

## Troubleshooting

### Common Issues
1. **Module Loading Failures**
   - Check kernel version compatibility
   - Verify module signing
   - Review dmesg for specific errors

2. **MCP Communication Issues**
   - Confirm kerneldev-mcp installation
   - Check Python environment compatibility  
   - Verify kernel headers installation

3. **Database Integration Problems**
   - Ensure Tortoise ORM connection
   - Check model field compatibility
   - Verify async/await usage

### Debug Commands
→ **[`scripts/debug.sh`](scripts/debug.sh)**

```bash
bash scripts/debug.sh [module_name]
```

---

## Contributing

### Adding New Templates
1. Create module in `templates/`
2. Add documentation in `examples/`
3. Update integration tests
4. Submit PR with security review

### Integration Extensions
- Database model extensions
- MalwareHunter Elite integration
- Session management enhancements
- Real-time alerting improvements

---

*This skill enables advanced kernel-space forensic capabilities while maintaining integration with the existing CyberSec investigation framework. All modules should be developed with security, safety, and forensic integrity as primary concerns.*