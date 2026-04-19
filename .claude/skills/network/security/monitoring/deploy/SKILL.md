---
name: security-monitoring-deploy
description: Network forensic reconnaissance. Active connection inventory, suspicious listeners, routing anomalies, DNS/mDNS analysis, ARP cache poisoning detection, firewall rule audit, and IOC infrastructure correlation.
model: sonnet
maxTurns: 30
tools:
  - Read
  - Bash
  - Glob
  - Grep
  - WebSearch
  - WebFetch
skills:
  - shared-memory
  - tls/sslkeylog
  - threats/mitre-attack-mapper
tags:
- network
- monitoring2
- network-recon
mitre_attack:
- T1059
- T1071
- T1562.004
- T1595
nist_csf: []
capec: []
---

# Network Recon

**Purpose:** Rapid network-state triage with IOC-first correlation. Establishes connection baseline, detects C2 channels, identifies rogue listeners, and maps network anomalies to MITRE techniques.

---

## Core Focus Areas

- **Active connections**: TCP/UDP state, established/listening inventory, raw socket holders
- **Suspicious listeners**: Unexpected ports, listeners bound to `0.0.0.0`, unusual services
- **DNS anomalies**: Unusual resolvers, DNS tunneling patterns, mDNS/LLMNR abuse
- **ARP/MAC layer**: ARP cache poisoning, duplicate MAC addresses, MITM indicators
- **Routing anomalies**: Unexpected routes, policy routing, tunnel interfaces
- **Firewall audit**: iptables/nftables/ufw rule gaps, unexpected ACCEPTs
- **IOC correlation**: Match active connections and DNS queries against known-bad infrastructure
- **Wireless**: Rogue AP detection, promiscuous mode interfaces, monitor interfaces

---

## Key Techniques & Tools

### Connection Inventory
```bash
# All TCP/UDP connections with process info
ss -tulpn 2>/dev/null
ss -tulpna 2>/dev/null | sort -k5 | head -50

# Established connections (potential C2)
ss -tnp state established 2>/dev/null | \
  awk 'NR>1 {print $5, $6, $7}' | sort | uniq -c | sort -rn | head -20

# Raw socket holders (packet capture / injection capability)
ss -a --raw 2>/dev/null | head -10

# Connections on non-standard high ports
ss -tnp state established 2>/dev/null | \
  awk 'NR>1 && $5 ~ /:[0-9]+$/ {port=$5; sub(/.*:/,"",port); if(port+0>1024 && port+0!=443 && port+0!=80) print}' | \
  sort | uniq -c | sort -rn | head -20

# netstat for legacy compatibility
netstat -tulpn 2>/dev/null | head -30
```

### IOC Infrastructure Correlation
```bash
# Extract all remote IPs from established connections
REMOTE_IPS=$(ss -tnp state established 2>/dev/null | \
  awk 'NR>1 {ip=$5; sub(/:[^:]*$/,"",ip); print ip}' | sort -u)

# Lookup each IP against IOC database
for ip in $REMOTE_IPS; do
  result=$(grep -r "$ip" ./cybersec-shared/intelligence/ioc-db.md 2>/dev/null | head -1)
  [ -n "$result" ] && echo "IOC MATCH: $ip → $result"
done

# Reverse DNS lookup for all remote IPs
echo "$REMOTE_IPS" | while read ip; do
  host "$ip" 2>/dev/null | grep "domain name" | head -1
done

# GeoIP / ASN lookup (requires geoiplookup or similar)
echo "$REMOTE_IPS" | while read ip; do
  geoiplookup "$ip" 2>/dev/null | head -1
done
```

### DNS Analysis
```bash
# Current DNS resolver configuration
cat /etc/resolv.conf 2>/dev/null
systemd-resolve --status 2>/dev/null | grep -E "(DNS Servers|DNSSEC|Link)" | head -10

# Active DNS queries (requires tcpdump or sshdump)
sudo tcpdump -i any -c 200 -n 'port 53' 2>/dev/null | \
  awk 'NF && /A\?|AAAA\?|TXT\?|MX\?/' | sort | uniq -c | sort -rn | head -30

# DNS cache inspection
systemd-resolve --statistics 2>/dev/null
resolvectl query --cache=yes google.com 2>/dev/null

# Long/high-entropy subdomains (DNS tunneling indicator)
sudo tcpdump -i any -c 500 -n 'port 53' 2>/dev/null | \
  grep -oE '[a-zA-Z0-9_-]{25,}\.[a-zA-Z0-9_.-]+' | sort | uniq -c | sort -rn | head -10

# mDNS/LLMNR traffic (lateral movement via name resolution)
sudo tcpdump -i any -c 100 -n 'port 5353 or port 5355' 2>/dev/null | head -20
```

### ARP & MAC Layer
```bash
# ARP cache — look for duplicate IPs or gateway MAC changes
arp -n 2>/dev/null
ip neigh show 2>/dev/null

# Detect ARP cache poisoning (same IP, multiple MACs or vice versa)
arp -n 2>/dev/null | awk 'NR>1 {print $3}' | sort | uniq -d | \
  while read mac; do
    echo "DUPLICATE MAC: $mac"
    arp -n | grep "$mac"
  done

# Monitor for ARP changes (static watch)
ip -s neigh 2>/dev/null | grep "STALE\|FAILED" | head -10

# Promiscuous mode interfaces (packet capture risk)
ip link 2>/dev/null | grep PROMISC
```

### Routing & Interfaces
```bash
# Full routing table
ip route show table all 2>/dev/null | head -30

# Policy routing (potential traffic interception)
ip rule list 2>/dev/null

# Tunnel interfaces (potential exfil or C2)
ip link show type gre 2>/dev/null
ip link show type tun 2>/dev/null
ip link show type wireguard 2>/dev/null
ip tunnel show 2>/dev/null

# Interfaces in unexpected states
ip link 2>/dev/null | grep -E "UNKNOWN|DORMANT|PROMISC|ALLMULTI"

# IPv6 — check for unexpected global addresses (privacy leak)
ip -6 addr show 2>/dev/null | grep "global"
```

### Firewall Audit
```bash
# iptables rules (all tables)
sudo iptables-save 2>/dev/null | grep -v "^#"
sudo ip6tables-save 2>/dev/null | grep -v "^#"

# nftables (modern replacement)
sudo nft list ruleset 2>/dev/null

# ufw status
sudo ufw status verbose 2>/dev/null

# Check for ACCEPT all rules (dangerous)
sudo iptables -L -n -v 2>/dev/null | grep -E "ACCEPT.*0\.0\.0\.0/0.*0\.0\.0\.0/0"

# Firewall logging — recent blocked connections
sudo iptables -L -n -v --line-numbers 2>/dev/null | grep -E "DROP|REJECT|LOG" | head -10
journalctl -k --since "1 hour ago" 2>/dev/null | grep -iE "(iptables|nft|DROP|REJECT)" | head -20
```

### Live Traffic Capture
```bash
# Quick capture for IOC correlation
sudo tcpdump -i any -c 1000 -n -w /tmp/quick_capture.pcap 2>/dev/null

# HTTP plaintext (C2 / exfil indicator)
sudo tcpdump -i any -c 500 -n -A 'tcp port 80' 2>/dev/null | \
  grep -E "(GET|POST|Host:|User-Agent:)" | head -20

# Non-standard HTTPS ports
sudo tcpdump -i any -c 200 -n 'tcp and not port 443 and not port 80' 2>/dev/null | \
  grep "Flags \[S\]" | awk '{print $3}' | sort | uniq -c | sort -rn | head -20

# Suricata alert log (if running)
tail -50 /var/log/suricata/fast.log 2>/dev/null
tail -20 /var/log/suricata/eve.json 2>/dev/null | python3 -m json.tool 2>/dev/null | \
  grep -E "(signature|src_ip|dest_ip|category)" | head -30
```

### Wireless Recon
```bash
# Wireless interfaces and mode
iwconfig 2>/dev/null | grep -E "(Mode|ESSID|Access Point|Freq|Rate)"
iw dev 2>/dev/null

# Monitor mode interfaces (unauthorized packet capture)
iw dev 2>/dev/null | grep "type monitor"

# Scan for rogue APs
sudo iw dev wlan0 scan 2>/dev/null | grep -E "(SSID|BSSID|signal|freq)" | head -20
```

---

## MITRE ATT&CK Mapping

| Finding | Technique |
|---------|-----------|
| Unexpected listener on high port | T1071 – Application Layer Protocol |
| DNS tunneling / long subdomains | T1071.004 – DNS |
| ARP cache poisoning | T1557.002 – ARP Cache Poisoning |
| Established connection to IOC IP | T1041 – Exfiltration Over C2 Channel |
| GRE/TUN tunnel interface | T1572 – Protocol Tunneling |
| Firewall rule disabled | T1562.004 – Disable or Modify System Firewall |
| Promiscuous mode interface | T1040 – Network Sniffing |
| mDNS/LLMNR response poisoning | T1557.001 – LLMNR/NBT-NS Poisoning |

---

## Rules for Agents

1. Always correlate all remote IPs against `ioc-db.md` before proceeding
2. Any connection to IOC-listed IP = **HIGH** minimum, escalate to CYBERSEC-AGENT
3. Unexpected listeners on ports < 1024 = **HIGH**
4. ARP cache with duplicate IPs = **MEDIUM+** MITM indicator
5. Tunnel interfaces not in NetworkBaseline = **HIGH**
6. Log all remote IPs, listening ports, and anomalous routes to `iocs.md`
7. Sync all network IOCs to shared memory at session end
