"""Forensic investigation API handlers: findings, IOCs, YARA, network, intelligence, audit, compliance, NIST."""
from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse


def _parse_pagination(request: Request, default_limit: int = 20) -> tuple[int, int]:
    """Parse page/limit query params."""
    page = int(request.query_params.get("page", 0))
    limit = int(request.query_params.get("limit", default_limit))
    return page, min(limit, 100)  # cap at 100


async def api_findings(request: Request) -> JSONResponse:
    """Security findings summary — totals by severity/status + recent."""
    try:
        from db.models.investigation import Finding
        total = await Finding.all().count()

        all_severities = await Finding.all().values_list("severity", flat=True)
        by_severity: dict[str, int] = {}
        for sev in all_severities:
            k = str(sev.value if hasattr(sev, "value") else sev) if sev else "unknown"
            by_severity[k] = by_severity.get(k, 0) + 1

        all_statuses = await Finding.all().values_list("status", flat=True)
        by_status: dict[str, int] = {}
        for st in all_statuses:
            k = str(st.value if hasattr(st, "value") else st) if st else "unknown"
            by_status[k] = by_status.get(k, 0) + 1

        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        last_24h = await Finding.filter(created_at__gte=now - datetime.timedelta(hours=24)).count()
        last_7d = await Finding.filter(created_at__gte=now - datetime.timedelta(days=7)).count()

        _FINDING_FIELDS = [
            "id", "title", "description", "severity", "status", "confidence",
            "location", "evidence", "evidence_hash", "command_output",
            "cross_validation", "next_action", "analyst_notes", "remediation",
            "resolved_at", "tags", "created_at", "updated_at", "is_active",
        ]
        page, limit = _parse_pagination(request, 20)
        offset = page * limit
        recent = await Finding.all().order_by("-created_at").offset(offset).limit(limit).values(*_FINDING_FIELDS)
        recent_list = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else (v.value if hasattr(v, "value") else v))
             for k, v in row.items()}
            for row in recent
        ]
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({
        "total": total,
        "by_severity": by_severity,
        "by_status": by_status,
        "trend": {"last_24h": last_24h, "last_7d": last_7d},
        "recent": recent_list,
    })


async def api_iocs(request: Request) -> JSONResponse:
    """IOC summary — totals by type/status/confidence + recent 20."""
    try:
        from db.models.investigation import IOC
        total = await IOC.all().count()

        all_rows = await IOC.all().values_list("ioc_type", "status", "confidence", flat=False)
        by_type: dict[str, int] = {}
        by_status: dict[str, int] = {}
        by_confidence: dict[str, int] = {}
        for ioc_type, status, confidence in all_rows:
            t = str(ioc_type) if ioc_type else "unknown"
            by_type[t] = by_type.get(t, 0) + 1
            s = str(status.value if hasattr(status, "value") else status) if status else "unknown"
            by_status[s] = by_status.get(s, 0) + 1
            c = str(confidence.value if hasattr(confidence, "value") else confidence) if confidence else "unknown"
            by_confidence[c] = by_confidence.get(c, 0) + 1

        _IOC_FIELDS = [
            "id", "ioc_id", "ioc_type", "value", "confidence", "status",
            "sightings", "context", "source", "evidence_hash", "tags",
            "created_at", "updated_at", "is_active",
        ]
        recent = await IOC.all().order_by("-updated_at").limit(20).values(*_IOC_FIELDS)
        recent_list = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else (v.value if hasattr(v, "value") else v))
             for k, v in row.items()}
            for row in recent
        ]
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({
        "total": total,
        "by_type": dict(sorted(by_type.items(), key=lambda x: -x[1])[:10]),
        "by_status": by_status,
        "by_confidence": by_confidence,
        "recent": recent_list,
    })


async def api_yara(request: Request) -> JSONResponse:
    """YARA rule summary — totals by status/severity/source + recent 10."""
    try:
        from db.models.yara_rule import YaraRule
        total = await YaraRule.all().count()

        all_rows = await YaraRule.all().values_list("status", "source", flat=False)
        by_status: dict[str, int] = {}
        by_source: dict[str, int] = {}
        for status, source in all_rows:
            s = str(status.value if hasattr(status, "value") else status) if status else "unknown"
            by_status[s] = by_status.get(s, 0) + 1
            src = str(source.value if hasattr(source, "value") else source) if source else "unknown"
            by_source[src] = by_source.get(src, 0) + 1

        _YARA_FIELDS = [
            "id", "rule_id", "name", "description", "content", "status", "source",
            "severity", "detection_count", "false_positive_rate",
            "test_results", "tags", "created_at", "updated_at",
        ]
        try:
            recent = await YaraRule.all().order_by("-created_at").limit(20).values(*_YARA_FIELDS)
        except Exception:
            recent = await YaraRule.all().order_by("-created_at").limit(20).values(
                "id", "rule_id", "name", "status", "source", "created_at"
            )
        recent_list = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else (v.value if hasattr(v, "value") else v))
             for k, v in row.items()}
            for row in recent
        ]
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({
        "total": total,
        "by_status": by_status,
        "by_source": by_source,
        "recent": recent_list,
    })


async def api_network(request: Request) -> JSONResponse:
    """Network assets summary — hosts and IP addresses with full fields."""
    try:
        from db.models.network import IPAddress, Host
        total_hosts = await Host.all().count()
        compromised = await Host.filter(is_compromised=True).count()
        targets = await Host.filter(is_target=True).count()
        total_ips = await IPAddress.all().count()
        private_ips = await IPAddress.filter(is_private=True).count()

        # Top countries by IP
        all_countries = await IPAddress.all().values_list("geo_country", flat=True)
        country_counts: dict[str, int] = {}
        for c in all_countries:
            if c:
                country_counts[c] = country_counts.get(c, 0) + 1
        top_countries = [
            {"code": code, "count": cnt}
            for code, cnt in sorted(country_counts.items(), key=lambda x: -x[1])[:10]
        ]

        recent_hosts = await Host.all().order_by("-created_at").limit(20).values(
            "id", "hostname", "os_name", "os_version", "architecture",
            "is_localhost", "is_target", "is_compromised", "notes", "created_at",
        )
        recent_hosts_list = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in row.items()}
            for row in recent_hosts
        ]

        recent_ips = await IPAddress.all().order_by("-last_seen_at").limit(20).values(
            "id", "address", "version", "is_private", "geo_country",
            "first_seen_at", "last_seen_at", "notes",
        )
        recent_ips_list = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in row.items()}
            for row in recent_ips
        ]
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({
        "hosts": {"total": total_hosts, "compromised": compromised, "targets": targets},
        "ip_addresses": {"total": total_ips, "private": private_ips, "public": total_ips - private_ips},
        "top_countries": top_countries,
        "recent_hosts": recent_hosts_list,
        "recent_ips": recent_ips_list,
    })


async def api_intelligence(request: Request) -> JSONResponse:
    """Threat intelligence database counts — MITRE, CVE, CWE, CAPEC."""
    try:
        from db.models.mitre_technique import MitreTechniqueIntel
        from db.models.cve_entry import CVEIntelligenceEntry
        from db.models.cwe import CWEIntel
        from db.models.capec import CapecAttackPatternIntel

        mitre_count = await MitreTechniqueIntel.all().count()
        cve_count = await CVEIntelligenceEntry.all().count()
        cwe_count = await CWEIntel.all().count()
        capec_count = await CapecAttackPatternIntel.all().count()

        tactics_raw = await MitreTechniqueIntel.all().values_list("tactics", flat=True)
        tactic_set: set[str] = set()
        for raw in tactics_raw:
            if isinstance(raw, list):
                tactic_set.update(str(t) for t in raw if t)
            elif raw:
                tactic_set.add(str(raw))
        unique_tactics = len(tactic_set)

        # Last seeded — check feed snapshot or update log
        last_seeded = None
        try:
            from db.models.feed_snapshot import FeedSnapshot
            snap = await FeedSnapshot.all().order_by("-created_at").first()
            last_seeded = snap.created_at.isoformat() if snap and snap.created_at else None
        except Exception:
            pass

        # Recent MITRE techniques with full fields
        _MITRE_FIELDS = [
            "id", "technique_id", "name", "description", "tactics",
            "platforms", "data_sources", "is_sub_technique", "parent_technique_id",
            "detection", "url", "tags", "created_at", "updated_at",
        ]
        recent_mitre = await MitreTechniqueIntel.all().order_by("-created_at").limit(10).values(*_MITRE_FIELDS)
        recent_mitre_list = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in row.items()}
            for row in recent_mitre
        ]

        # Recent CVE entries with full fields
        _CVE_FIELDS = ["id", "cve_id", "cvss_score", "severity", "description",
                       "exploit_available", "patch_available", "published_at", "tags", "created_at"]
        try:
            from db.models.cve import CVEIntel
            recent_cve = await CVEIntel.all().order_by("-published_at").limit(10).values(*_CVE_FIELDS)
        except Exception:
            recent_cve = []
        recent_cve_list = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else (v.value if hasattr(v, "value") else v))
             for k, v in row.items()}
            for row in recent_cve
        ]
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({
        "mitre": {"techniques": mitre_count, "tactics": unique_tactics},
        "cve": {"total": cve_count},
        "cwe": {"total": cwe_count},
        "capec": {"total": capec_count},
        "last_seeded": last_seeded,
        "recent_mitre": recent_mitre_list,
        "recent_cve": recent_cve_list,
    })


async def api_audit(request: Request) -> JSONResponse:
    """Audit log summary — recent entries and action counts."""
    try:
        from db.models.audit import AuditLog
        import datetime as _dt

        total = await AuditLog.all().count()
        _AUDIT_FIELDS = [
            "id", "action", "entity_type", "entity_id", "entity_repr",
            "agent", "resource", "ip_address", "old_value", "new_value",
            "metadata", "created_at",
        ]
        recent = await AuditLog.all().order_by("-created_at").limit(50).values(*_AUDIT_FIELDS)

        recent_list = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else (v.value if hasattr(v, "value") else v))
             for k, v in row.items()}
            for row in recent
        ]

        # Count by action
        by_action: dict[str, int] = {}
        for e in recent_list:
            a = e.get("action") or "unknown"
            by_action[a] = by_action.get(a, 0) + 1

        # Count by agent
        by_agent: dict[str, int] = {}
        for e in recent_list:
            ag = e.get("agent") or "unknown"
            by_agent[ag] = by_agent.get(ag, 0) + 1

        cutoff = _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(hours=1)
        last_hour_count = await AuditLog.filter(created_at__gte=cutoff).count()
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({
        "total": total,
        "last_hour_count": last_hour_count,
        "by_action": by_action,
        "by_agent": by_agent,
        "recent": recent_list,
    })


async def api_compliance(request: Request) -> JSONResponse:
    """Compliance rules summary — totals by framework and severity + recent rules."""
    try:
        from db.models.compliance import ComplianceRule
        total = await ComplianceRule.all().count()

        all_rules = await ComplianceRule.all().values_list("framework", "severity")
        by_framework: dict[str, int] = {}
        by_severity: dict[str, int] = {}
        for framework, severity in all_rules:
            f = framework or "unknown"
            by_framework[f] = by_framework.get(f, 0) + 1
            s = severity if isinstance(severity, str) else (severity.value if severity else "unknown")
            by_severity[s] = by_severity.get(s, 0) + 1

        _COMPLIANCE_FIELDS = [
            "id", "rule_id", "title", "description", "framework", "severity",
            "check_procedures", "remediation_steps", "evidence_requirements",
            "retention_period_days", "audit_frequency", "created_at", "updated_at",
        ]
        recent = await ComplianceRule.all().order_by("-created_at").limit(20).values(*_COMPLIANCE_FIELDS)
        recent_list = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else (v.value if hasattr(v, "value") else v))
             for k, v in row.items()}
            for row in recent
        ]
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({
        "total": total,
        "by_framework": dict(sorted(by_framework.items(), key=lambda x: -x[1])),
        "by_severity": by_severity,
        "recent": recent_list,
    })


async def api_nist_csf(request: Request) -> JSONResponse:
    """NIST CSF 2.0 controls — totals by function/category + recent controls."""
    try:
        from db.models.nist_csf import NistCsfControl
        total = await NistCsfControl.all().count()
        if total == 0:
            return JSONResponse({"total": 0, "note": "Run: python3 manage.py seed-nist-csf"})
        rows = await NistCsfControl.all().values_list("function", "function_code", "category")
        by_function: dict[str, int] = {}
        by_category: dict[str, int] = {}
        for fn, _fc, cat in rows:
            by_function[fn] = by_function.get(fn, 0) + 1
            by_category[cat] = by_category.get(cat, 0) + 1

        # Full fields for recent controls
        _CSF_FIELDS = list(NistCsfControl._meta.fields_map.keys())
        _CSF_SCALAR = [f for f in _CSF_FIELDS
                       if type(NistCsfControl._meta.fields_map[f]).__name__ not in (
                           "ForeignKeyFieldInstance", "ManyToManyFieldInstance",
                           "BackwardsOneToOneRelation", "BackwardsFKRelation",
                       )]
        recent = await NistCsfControl.all().order_by("function_code").limit(20).values(*_CSF_SCALAR)
        recent_list = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in row.items()}
            for row in recent
        ]
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({
        "total": total,
        "by_function": dict(sorted(by_function.items())),
        "by_category": dict(sorted(by_category.items(), key=lambda x: -x[1])),
        "recent": recent_list,
    })


async def api_nist_ai_rmf(request: Request) -> JSONResponse:
    """NIST AI RMF 1.0 controls — totals by function/topic + recent controls."""
    try:
        from db.models.nist_ai_rmf import NistAiRmfControl
        total = await NistAiRmfControl.all().count()
        if total == 0:
            return JSONResponse({"total": 0, "note": "Run: python3 manage.py seed-nist-ai-rmf"})
        rows = await NistAiRmfControl.all().values_list("function", "topic")
        by_function: dict[str, int] = {}
        by_topic: dict[str, int] = {}
        for fn, topic in rows:
            by_function[fn] = by_function.get(fn, 0) + 1
            t = topic or "general"
            by_topic[t] = by_topic.get(t, 0) + 1

        _RMF_FIELDS = list(NistAiRmfControl._meta.fields_map.keys())
        _RMF_SCALAR = [f for f in _RMF_FIELDS
                       if type(NistAiRmfControl._meta.fields_map[f]).__name__ not in (
                           "ForeignKeyFieldInstance", "ManyToManyFieldInstance",
                           "BackwardsOneToOneRelation", "BackwardsFKRelation",
                       )]
        recent = await NistAiRmfControl.all().order_by("function").limit(20).values(*_RMF_SCALAR)
        recent_list = [
            {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in row.items()}
            for row in recent
        ]
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e)})
    return JSONResponse({
        "total": total,
        "by_function": dict(sorted(by_function.items())),
        "by_topic": dict(sorted(by_topic.items(), key=lambda x: -x[1])),
        "recent": recent_list,
    })


# ── Findings CRUD ─────────────────────────────────────────────────────────────

async def api_findings_create(request: Request) -> JSONResponse:
    """POST /api/findings — create a new finding."""
    try:
        from db.models.investigation import Finding
        body = await request.json()
        title = (body.get("title") or "").strip()
        if not title:
            return JSONResponse({"error": "title is required"}, status_code=400)
        finding = await Finding.create(
            title=title,
            description=body.get("description", ""),
            severity=body.get("severity", "medium"),
            status=body.get("status", "open"),
            confidence=body.get("confidence", "medium"),
            location=body.get("location"),
            evidence=body.get("evidence"),
            analyst_notes=body.get("analyst_notes", ""),
            remediation=body.get("remediation", ""),
            tags=body.get("tags", []),
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True, "id": finding.id}, status_code=201)


async def api_findings_update(request: Request) -> JSONResponse:
    """PATCH /api/findings/{id} — update a finding."""
    try:
        from db.models.investigation import Finding
        finding_id = int(request.path_params["id"])
        finding = await Finding.get_or_none(id=finding_id)
        if finding is None:
            return JSONResponse({"error": "not found"}, status_code=404)
        body = await request.json()
        for field in ("title", "description", "severity", "status", "confidence",
                      "location", "evidence", "analyst_notes", "remediation", "tags", "next_action"):
            if field in body:
                setattr(finding, field, body[field])
        await finding.save()
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True, "id": finding_id})


async def api_findings_delete(request: Request) -> JSONResponse:
    """DELETE /api/findings/{id} — delete a finding."""
    try:
        from db.models.investigation import Finding
        finding_id = int(request.path_params["id"])
        deleted = await Finding.filter(id=finding_id).delete()
        if not deleted:
            return JSONResponse({"error": "not found"}, status_code=404)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True})


# ── IOC CRUD ──────────────────────────────────────────────────────────────────

async def api_iocs_create(request: Request) -> JSONResponse:
    """POST /api/iocs — create a new IOC."""
    try:
        import uuid
        from db.models.investigation import IOC
        body = await request.json()
        value = (body.get("value") or "").strip()
        ioc_type = (body.get("ioc_type") or "").strip()
        if not value or not ioc_type:
            return JSONResponse({"error": "value and ioc_type are required"}, status_code=400)
        ioc = await IOC.create(
            ioc_id=body.get("ioc_id") or str(uuid.uuid4())[:8],
            ioc_type=ioc_type,
            value=value,
            confidence=body.get("confidence", "low"),
            status=body.get("status", "active"),
            source=body.get("source"),
            context=body.get("context", {}),
            tags=body.get("tags", []),
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True, "id": ioc.id}, status_code=201)


async def api_iocs_update(request: Request) -> JSONResponse:
    """PATCH /api/iocs/{id} — update an IOC."""
    try:
        from db.models.investigation import IOC
        ioc_id = int(request.path_params["id"])
        ioc = await IOC.get_or_none(id=ioc_id)
        if ioc is None:
            return JSONResponse({"error": "not found"}, status_code=404)
        body = await request.json()
        for field in ("ioc_type", "value", "confidence", "status", "source", "context", "tags", "sightings"):
            if field in body:
                setattr(ioc, field, body[field])
        await ioc.save()
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True, "id": ioc_id})


async def api_iocs_delete(request: Request) -> JSONResponse:
    """DELETE /api/iocs/{id} — delete an IOC."""
    try:
        from db.models.investigation import IOC
        ioc_id = int(request.path_params["id"])
        deleted = await IOC.filter(id=ioc_id).delete()
        if not deleted:
            return JSONResponse({"error": "not found"}, status_code=404)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True})


# ── Investigations CRUD ───────────────────────────────────────────────────────

async def api_investigations_create(request: Request) -> JSONResponse:
    """POST /api/investigations — create a new case session."""
    try:
        import uuid
        from db.models.scope import Project, Session
        body = await request.json()
        name = (body.get("name") or "").strip()
        if not name:
            return JSONResponse({"error": "name is required"}, status_code=400)
        # Use first active project or create default
        project = await Project.filter(is_active=True).first()
        if project is None:
            project = await Project.create(name="Default", description="Auto-created")
        session = await Session.create(
            project=project,
            session_id=str(uuid.uuid4()),
            name=name,
            description=body.get("description", ""),
            agent=body.get("agent", "cybersec-agent"),
            mode=body.get("mode", "blue"),
            phase=body.get("phase", "init"),
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True, "id": session.id}, status_code=201)


async def api_investigations_update(request: Request) -> JSONResponse:
    """PATCH /api/investigations/{id} — update an investigation session."""
    try:
        from db.models.scope import Session
        inv_id = int(request.path_params["id"])
        session = await Session.get_or_none(id=inv_id)
        if session is None:
            return JSONResponse({"error": "not found"}, status_code=404)
        body = await request.json()
        for field in ("name", "description", "agent", "mode", "phase", "is_active"):
            if field in body:
                setattr(session, field, body[field])
        await session.save()
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True, "id": inv_id})


async def api_investigations_delete(request: Request) -> JSONResponse:
    """DELETE /api/investigations/{id} — soft-delete an investigation."""
    try:
        import datetime
        from db.models.scope import Session
        inv_id = int(request.path_params["id"])
        session = await Session.get_or_none(id=inv_id)
        if session is None:
            return JSONResponse({"error": "not found"}, status_code=404)
        session.is_active = False
        session.deleted_at = datetime.datetime.now(datetime.timezone.utc)
        await session.save()
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    return JSONResponse({"ok": True})
