---
name: scope-session-detect
description: Per-session ephemeral forensic layer. Real-time IOC detection, live threat monitoring, active defense coordination, and evidence preservation during active investigation sessions in ./cybersec-sessions/YYYYMMDD_HHMMSS/.
model: sonnet
maxTurns: 20
tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - cybersec
tags:
- ops
- scope
- session
- scope-session
mitre_attack:
- T1059
nist_csf: []
capec: []
---

# Session Layer Skill – Real-Time Forensic Operations

**Purpose:**  
Lowest layer in the hierarchy. Provides real-time forensic analysis, live threat detection, active defense coordination, and immediate hardening responses during active investigation sessions. Manages ephemeral data with immediate threat response capabilities.

**Storage Location:**  
`./cybersec-sessions/$(date +%Y%m%d_%H%M%S)/`


## Session-Specific IOC Processing

### 🚨 **Live IOC Detection Pipeline**
| Detection Phase  | Real-Time Action          | Response Time | Escalation Trigger    |
|------------------|---------------------------|---------------|-----------------------|
| IOC Recognition  | Immediate alert + log     | < 1 second    | High confidence match |
| Context Analysis | Threat assessment         | < 5 seconds   | Critical severity     |
| Cross-Validation | Multi-source verification | < 10 seconds  | Confirmed threat      |
| Response Action  | Blocking/containment      | < 30 seconds  | Active compromise     |

### 📊 **Real-Time Threat Assessment**
- **Confidence scoring**: Live confidence calculation for all indicators
- **Severity escalation**: Real-time severity assessment and escalation
- **Attack progression**: Live tracking of attack chain progression
- **Impact assessment**: Real-time assessment of potential impact
- **Response prioritization**: Live prioritization of response actions

---

## Automatic Behavior

### Real-Time Monitoring Loop

```bash
# Live threat detection and response loop (conceptual)
monitor_live_threats() {
  while [ "$SESSION_ACTIVE" = "true" ]; do
    # Network IOC monitoring
    check_network_iocs
    
    # Process IOC monitoring  
    check_process_iocs
    
    # Memory IOC monitoring
    check_memory_iocs
    
    # File system IOC monitoring
    check_filesystem_iocs
    
    # Anti-forensic detection
    detect_anti_forensic_activity
    
    # Response coordination
    coordinate_active_responses
    
    sleep 1  # 1-second monitoring cycle
  done
}
```

### On Session End (LIVE SYNC)
1. **Preserve live capture data** → archive all real-time monitoring data
2. **Sync detected IOCs** → merge session IOCs with project and system layers
3. **Archive response actions** → document all defensive actions taken
4. **Update threat intelligence** → enhance project threat profiles
5. **Preserve forensic timeline** → complete timeline documentation
6. **Sync hardening changes** → document-applied hardening measures

---

## Session File Structure

```
./cybersec-sessions/YYYYMMDD_HHMMSS/
├── live/
│   ├── active-iocs.txt       ← Real-time IOC matching database
│   ├── network-monitor.log   ← Live network traffic analysis
│   ├── process-monitor.log   ← Live process behavior tracking
│   ├── memory-monitor.log    ← Live memory analysis results
│   ├── filesystem-watch.log  ← Real-time file system monitoring
│   └── threat-alerts.log     ← Live threat detection alerts
├── analysis/
│   ├── behavioral.md         ← Real-time behavioral analysis
│   ├── network-forensics.md  ← Session network forensics
│   ├── memory-forensics.md   ← Session memory forensics
│   ├── malware-analysis.md   ← Live malware analysis results
│   └── timeline-live.md      ← Real-time timeline construction
├── response/
│   ├── actions-taken.md      ← Defensive actions implemented
│   ├── blocking-rules.md     ← IOC-based blocking implemented
│   ├── containment.md        ← Threat containment measures
│   ├── escalations.md        ← Threat escalation decisions
│   └── emergency-response.md ← Emergency response activations
├── hardening/
│   ├── applied.md            ← Hardening measures applied this session
│   ├── emergency.md          ← Emergency hardening activations
│   ├── progressive.md        ← Progressive hardening responses
│   ├── configuration.md      ← Live configuration changes
│   └── mitigation.md         ← Threat-specific mitigations applied
├── artifacts/
│   ├── network/              ← Network captures and analysis
│   ├── memory/               ← Memory dumps and analysis
│   ├── processes/            ← Process artifacts and analysis
│   ├── files/                ← File system artifacts
│   ├── logs/                 ← Log captures and analysis
│   └── malware/              ← Malware samples and analysis
├── anti-forensics/
│   ├── evasion-detected.md   ← Anti-forensic techniques detected
│   ├── evidence-tampering.md ← Evidence tampering attempts
│   ├── steganography.md      ← Hidden data detection results
│   ├── obfuscation.md        ← Code/data obfuscation analysis
│   └── countermeasures.md    ← Anti-forensic countermeasures applied
└── meta/
    ├── session-manifest.json ← Session metadata and configuration
    ├── iocs.md               ← Session IOCs discovered
    ├── timeline.md           ← Complete session timeline
    ├── findings.md           ← Session findings summary
    └── session.log           ← Complete session activity log
```

---

## Real-Time Threat Detection
## Cross-Layer Real-Time Integration

### 📤 **Live Escalation to Project Layer**
- **Critical IOCs**: Immediate escalation of high-confidence indicators
- **Threat patterns**: Real-time threat pattern sharing
- **Attack campaigns**: Live attack campaign correlation
- **Evidence alerts**: Immediate evidence preservation alerts

### 📥 **Live Intelligence from Project Layer**
- **IOC updates**: Real-time IOC database updates
- **Threat intel**: Live threat intelligence feeds
- **Response procedures**: Project-specific response playbooks
- **Hardening requirements**: Real-time hardening requirement updates

### 🔄 **Live System Layer Integration**
- **Global threat alerts**: Real-time global threat notifications
- **Hardware security**: Live hardware security monitoring
- **Firmware integrity**: Real-time firmware integrity verification
- **Cryptographic validation**: Live cryptographic integrity verification

---

## Rules for Agents

1. **Maintain real-time responsiveness** – all analysis under 30-second response time
2. **Preserve evidence integrity** throughout all live operations
3. **Coordinate with defense systems** for immediate threat response
4. **Document all actions** with precise timestamps and chain of custody
5. **Escalate immediately** upon detection of critical threats
6. **Apply progressive hardening** based on live threat assessment
7. **Validate all IOCs** with multiple sources before high-confidence classification
8. **Monitor anti-forensic activity** continuously during investigation
9. **Maintain session isolation** while coordinating with project/system layers
10. **Prepare for emergency response** with all necessary evidence preserved

---

**Ready for real-time forensic operations with active threat response.**