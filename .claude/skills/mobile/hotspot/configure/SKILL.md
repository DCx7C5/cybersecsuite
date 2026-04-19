---
name: hotspot-configure
description: >
  Configure mobile hotspot or rogue access point for network interception, traffic analysis, or red-team MITM exercises.
domain: cybersecurity
subdomain: mobile-security
tags: [mobile, hotspot, wifi, intercept, configure]
nist_csf: [PR.AC-05]
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack: [T1557]
capec: []
---

# Hotspot Configure

## Overview

Configure a mobile hotspot or rogue AP for traffic interception and network analysis. Use only in authorized penetration testing or forensic environments.

## Procedure

### Linux softAP via hostapd

```bash
# Install
apt install hostapd dnsmasq -y

# Configure hostapd.conf
cat > /tmp/hostapd.conf <<'HEOF'
interface=wlan0
driver=nl80211
ssid=TestNetwork
hw_mode=g
channel=6
wmm_enabled=0
auth_algs=1
ignore_broadcast_ssid=0
HEOF

hostapd /tmp/hostapd.conf &
```

### Enable IP forwarding

```bash
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```

## MITRE ATT&CK

| Technique | Name |
|-----------|------|
| T1557 | Adversary-in-the-Middle |
