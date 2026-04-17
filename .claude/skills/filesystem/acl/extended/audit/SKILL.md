---
name: acl-extended-audit
description: >
  Audit POSIX extended ACLs (getfacl) and SELinux/AppArmor file contexts to verify least-privilege access control and detect unexpected permission grants.
action: audit
domain: cybersecurity
subdomain: filesystem-security
tags:
  - acl
  - getfacl
  - selinux
  - apparmor
  - least-privilege
  - access-control
nist_csf:
  - PR.AC-04
  - ID.RA-01
---
