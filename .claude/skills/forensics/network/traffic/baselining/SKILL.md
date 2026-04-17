---
name: network-traffic-baselining
description: Build network traffic baselines from NetFlow/IPFIX data using Python pandas for statistical analysis, z-score
action: baselining
  anomaly detection, and hourly/daily traffic pattern profiling
domain: cybersecurity
subdomain: network-security
tags:
- netflow
- ipfix
- traffic-analysis
- baselining
- anomaly-detection
- pandas
- network-monitoring
nist_csf:
- PR.IR-01
- DE.CM-01
- ID.AM-03
- PR.DS-02
model: sonnet
maxTurns: 20
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1059
capec: []
---

# Implementing Network Traffic Baselining

## Overview

Network traffic baselining establishes normal communication patterns by analyzing historical NetFlow/IPFIX data to create statistical profiles of expected behavior. This skill uses Python pandas to compute hourly and daily traffic distributions, per-host byte/packet counts, protocol ratios, and top-N talker profiles. Anomalies are detected using z-score thresholds and IQR (interquartile range) outlier methods, enabling SOC analysts to identify deviations such as data exfiltration spikes, beaconing patterns, and unusual port usage.


## When to Use

- When deploying or configuring implementing network traffic baselining capabilities in your environment
- When establishing security controls aligned to compliance requirements
- When building or improving security architecture for this domain
- When conducting security assessments that require this implementation

## Prerequisites

- NetFlow v5/v9 or IPFIX flow data exported as CSV or JSON
- Python 3.8+ with pandas and numpy libraries
- Historical flow data (minimum 7 days recommended for baseline)

## Steps

1. Ingest NetFlow/IPFIX records from CSV or JSON exports
2. Compute hourly and daily traffic volume distributions (bytes, packets, flows)
3. Build per-source-IP baseline profiles with mean, median, standard deviation
4. Calculate protocol and port distribution baselines
5. Apply z-score anomaly detection to identify statistical outliers
6. Flag flows exceeding IQR-based thresholds as potential anomalies
7. Generate baseline report with anomaly alerts

## Expected Output

JSON report containing traffic baselines (hourly/daily profiles), per-host statistics, detected anomalies with z-scores, and top talker rankings with deviation indicators.


---

## CyberSecSuite Integration

```bash
# Open a case before starting investigation
mcp__cybersec__case_open --title "baselining" --type investigation

# Persist findings to PostgreSQL
mcp__cybersec__add_finding --title "..." --severity high --description "..."

# Log IOCs
mcp__cybersec__add_ioc --type domain --value "..." --confidence 0.9

# Map to MITRE
mcp__cybersec__suggest_mitre --description "..."
```

**Agent:** `@cybersec-agent` → delegates to appropriate specialist
