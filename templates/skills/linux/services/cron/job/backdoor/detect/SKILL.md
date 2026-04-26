
---
name: services-cron-job-backdoor-detect
description: Detect cron job backdoors — enumerate all crontab locations (/etc/cron*, /var/spool/cron), identify unusual jobs, detect cron file modification, and audit cron permissions.
domain: cybersecurity
subdomain: persistence-detection
tags:
- linux
- cron
- crontab
- backdoor
- persistence
nist_csf:
- DE.CM-01
- DE.AE-02
model: sonnet
maxTurns: 15
tools: [Read, Bash, Glob, Grep]
mitre_attack:
- T1053.003
capec: []
