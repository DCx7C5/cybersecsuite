"""
Cybersecurity A2A Agent — concrete implementation wired to the cybersecsuite.
Handles cybersecurity tasks: CVE lookup, IOC analysis, MITRE ATT&CK, artifacts.
Fully integrated with db ORM models and crypto signing.
"""
from __future__ import annotations

from typing import Optional
from datetime import datetime, timezone

from a2a.agent import BaseA2AAgent
from a2a.models import (
    AgentCard, AgentCapabilities, AgentAuthentication,
    AgentSkill, Task, Message, TaskArtifact, DataPart, TextPart,
)
from a2a.enums import PartType, AuthScheme
from a2a.task_store import TaskStore
from crypto import ArtifactManager


def build_cybersec_agent_card(base_url: str = "http://localhost:8000") -> AgentCard:
    """Build the AgentCard for the cybersec agent."""
    return AgentCard(
        name="CybersecAgent",
        description="Cybersecurity AI agent — CVE analysis, IOC hunting, threat intelligence, artifact signing.",
        url=base_url,
        version="1.0.0",
        capabilities=AgentCapabilities(
            streaming=True,
            push_notifications=False,
            state_transition_history=True,
        ),
        authentication=AgentAuthentication(
            schemes=[AuthScheme.ED25519, AuthScheme.BEARER],
        ),
        default_input_modes=["text/plain", "application/json"],
        default_output_modes=["text/plain", "application/json"],
        skills=[
            AgentSkill(
                id="cve-lookup",
                name="CVE Lookup",
                description="Look up CVE details, CVSS scores, and affected packages.",
                tags=["cve", "vulnerability", "nvd"],
                examples=["What is CVE-2024-1234?", "Show CVSS for CVE-2023-44487"],
            ),
            AgentSkill(
                id="ioc-analysis",
                name="IOC Analysis",
                description="Analyze indicators of compromise — IPs, domains, hashes, URLs.",
                tags=["ioc", "threat-intel", "malware"],
                examples=["Analyze IP 1.2.3.4", "Check hash abc123..."],
            ),
            AgentSkill(
                id="mitre-attack",
                name="MITRE ATT&CK",
                description="Query MITRE ATT&CK techniques, tactics, and threat actors.",
                tags=["mitre", "attack", "ttp"],
                examples=["What techniques does APT28 use?", "Describe T1059"],
            ),
            AgentSkill(
                id="artifact-sign",
                name="Artifact Signing",
                description="Sign and verify artifacts with Ed25519 signatures.",
                tags=["artifact", "signing", "crypto"],
                examples=["Sign this config", "Verify artifact integrity"],
            ),
            AgentSkill(
                id="threat-model",
                name="Threat Modeling",
                description="Generate threat models and attack surface analysis.",
                tags=["threat-model", "risk", "analysis"],
                examples=["Model threats for a web API", "Identify attack surface"],
            ),
        ],
        provider={"name": "cybersecsuite", "url": base_url},
    )


class CybersecA2AAgent(BaseA2AAgent):
    """
    Concrete cybersecurity A2A agent.

    Routes incoming tasks to the appropriate skill handler.
    Integrated with Tortoise ORM models and crypto signing.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        store: Optional[TaskStore] = None,
        artifact_manager: Optional["ArtifactManager"] = None,
    ) -> None:
        card = build_cybersec_agent_card(base_url)
        super().__init__(card=card, store=store)
        self._artifact_manager = artifact_manager

    def _get_artifact_manager(self) -> "ArtifactManager":
        """Lazy-load ArtifactManager with crypto signer."""
        if self._artifact_manager is None:
            from crypto import ArtifactManager, SSLArtifactSigner
            signer = SSLArtifactSigner()
            self._artifact_manager = ArtifactManager(signer)
        return self._artifact_manager

    async def execute(self, task: Task, message: Message) -> None:
        """Route task to skill handler based on message content."""
        text = self._extract_text(message).lower()

        try:
            if any(kw in text for kw in ("cve-", "cve ", "vulnerability")):
                await self._handle_cve(task, text)
            elif any(kw in text for kw in ("ioc", "ip ", "hash", "domain", "url")):
                await self._handle_ioc(task, text)
            elif any(kw in text for kw in ("mitre", "att&ck", "technique", "t1")):
                await self._handle_mitre(task, text)
            elif any(kw in text for kw in ("sign", "verify", "artifact")):
                await self._handle_artifact(task, text)
            elif any(kw in text for kw in ("threat model", "attack surface", "risk")):
                await self._handle_threat_model(task, text)
            else:
                self._reply(task.id, f"Received: {text}\n\nAvailable skills: cve-lookup, ioc-analysis, mitre-attack, artifact-sign, threat-model.")
        except Exception as e:
            self._fail(task.id, f"Agent error: {e}")

        # Persist task to DB after execution
        await self.store.persist_task(
            self.store.get(task.id) or task
        )

    # ── Skill Handlers ────────────────────────────────────────────────────────

    async def _handle_cve(self, task: Task, text: str) -> None:
        """CVE lookup skill — queries CVE ORM model."""
        import re
        from db.models.cve import CVEIntel as CVEEntry

        cve_pattern = re.compile(r"cve-\d{4}-\d{4,}", re.IGNORECASE)
        match = cve_pattern.search(text)

        results = []
        if match:
            cve_id = match.group(0).upper()
            entry = await CVEEntry.get_or_none(cve_id=cve_id)
            if entry:
                results.append({
                    "cve_id": entry.cve_id,
                    "description": entry.description,
                    "cvss_score": float(entry.cvss_score) if hasattr(entry, "cvss_score") and entry.cvss_score else None,
                    "severity": entry.severity if hasattr(entry, "severity") else None,
                    "published": entry.published_at.isoformat() if hasattr(entry, "published_at") and entry.published_at else None,
                })
        else:
            # Return recent CVEs
            entries = await CVEEntry.all().order_by("-created_at").limit(5)
            for entry in entries:
                results.append({
                    "cve_id": entry.cve_id,
                    "description": getattr(entry, "description", ""),
                })

        self.store.add_artifact(task.id, TaskArtifact(
            name="cve-result",
            parts=[DataPart(type=PartType.DATA, data={"cves": results, "query": text})],
        ))
        count = len(results)
        self._reply(task.id, f"CVE lookup complete. Found {count} result(s).")

    async def _handle_ioc(self, task: Task, text: str) -> None:
        """IOC analysis skill — queries IOC ORM model."""
        from db.models.investigation import IOC

        # Search IOCs by value substring
        iocs = await IOC.filter(is_active=True).order_by("-updated_at").limit(20)
        matches = []
        for ioc in iocs:
            if ioc.value and any(token in ioc.value.lower() for token in text.split() if len(token) > 3):
                matches.append({
                    "ioc_id": ioc.ioc_id,
                    "type": ioc.ioc_type,
                    "value": ioc.value,
                    "confidence": ioc.confidence.value if ioc.confidence else None,
                    "status": ioc.status.value if ioc.status else None,
                    "sightings": ioc.sightings,
                })

        if not matches:
            # Return recent active IOCs
            for ioc in iocs[:5]:
                matches.append({
                    "ioc_id": ioc.ioc_id,
                    "type": ioc.ioc_type,
                    "value": ioc.value,
                    "confidence": ioc.confidence.value if ioc.confidence else None,
                    "status": ioc.status.value if ioc.status else None,
                })

        self.store.add_artifact(task.id, TaskArtifact(
            name="ioc-result",
            parts=[DataPart(type=PartType.DATA, data={"iocs": matches, "query": text})],
        ))
        self._reply(task.id, f"IOC analysis complete. Found {len(matches)} indicator(s).")

    async def _handle_mitre(self, task: Task, text: str) -> None:
        """MITRE ATT&CK skill — queries MITRETechnique ORM model."""
        import re
        from db.models.investigation import MITRETechnique

        # Look for technique ID pattern (T1059, T1059.001)
        tech_pattern = re.compile(r"t\d{4}(?:\.\d{3})?", re.IGNORECASE)
        match = tech_pattern.search(text)

        results = []
        if match:
            tech_id = match.group(0).upper()
            techniques = await MITRETechnique.filter(technique_id=tech_id).limit(5)
            for t in techniques:
                results.append({
                    "technique_id": t.technique_id,
                    "name": t.name,
                    "tactic": t.tactic,
                    "description": t.description[:200] if t.description else "",
                })
        else:
            # Search by keyword in name/description
            techniques = await MITRETechnique.all().order_by("technique_id").limit(10)
            for t in techniques:
                if any(kw in (t.name or "").lower() or kw in (t.description or "").lower()
                       for kw in text.split() if len(kw) > 3):
                    results.append({
                        "technique_id": t.technique_id,
                        "name": t.name,
                        "tactic": t.tactic,
                    })

        self.store.add_artifact(task.id, TaskArtifact(
            name="mitre-result",
            parts=[DataPart(type=PartType.DATA, data={"techniques": results, "query": text})],
        ))
        self._reply(task.id, f"MITRE ATT&CK lookup complete. Found {len(results)} technique(s).")

    async def _handle_artifact(self, task: Task, text: str) -> None:
        """Artifact signing/verification skill — uses crypto.ArtifactManager + DB model."""
        mgr = self._get_artifact_manager()

        if "verify" in text:
            # Verify all recent artifacts
            from db.models.artifact import Artifact
            recent = await Artifact.all().order_by("-updated_at").limit(5)
            verify_results = []
            for art in recent:
                result = await mgr.verify_artifact(art.id)
                verify_results.append(result)

            self.store.add_artifact(task.id, TaskArtifact(
                name="verification-result",
                parts=[DataPart(type=PartType.DATA, data={"verifications": verify_results})],
            ))
            self._reply(task.id, f"Verified {len(verify_results)} artifact(s).")
        else:
            # Sign a new artifact
            payload = {"task_id": task.id, "content": text, "timestamp": datetime.now(timezone.utc).isoformat()}
            artifact = await mgr.create_artifact(
                name=f"a2a-task-{task.id[:8]}",
                content=payload,
                description=f"Signed via A2A task {task.id}",
                created_by="a2a-agent",
                reason="A2A artifact-sign skill",
            )

            self.store.add_artifact(task.id, TaskArtifact(
                name="signed-artifact",
                parts=[DataPart(
                    type=PartType.DATA,
                    data={
                        "artifact_id": artifact.id,
                        "content_hash": artifact.content_hash,
                        "signature_valid": artifact.signature_valid,
                        "key_id": artifact.key_id,
                        "version": artifact.version,
                    },
                )],
            ))
            self._reply(task.id, f"Artifact signed. ID: {artifact.id}, hash: {artifact.content_hash[:16]}...")

    async def _handle_threat_model(self, task: Task, text: str) -> None:
        """Threat modeling skill — queries Findings and Risks from DB."""
        from db.models.investigation import Finding, Risk

        # Gather recent findings and risks for context
        findings = await Finding.filter(is_active=True).order_by("-updated_at").limit(10)
        risks = await Risk.filter(is_active=True).order_by("-updated_at").limit(10)

        findings_data = [
            {"title": f.title, "severity": f.severity.value if f.severity else None, "status": f.status.value if f.status else None}
            for f in findings
        ]
        risks_data = [
            {"risk_id": r.risk_id, "title": r.title, "impact": r.impact, "likelihood": r.likelihood}
            for r in risks
        ]

        self.store.add_artifact(task.id, TaskArtifact(
            name="threat-model",
            parts=[DataPart(type=PartType.DATA, data={
                "query": text,
                "active_findings": findings_data,
                "active_risks": risks_data,
                "finding_count": len(findings_data),
                "risk_count": len(risks_data),
            })],
        ))
        self._reply(task.id, f"Threat model generated. {len(findings_data)} findings, {len(risks_data)} risks in context.")

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_text(message: Message) -> str:
        """Extract plain text from message parts."""
        parts = []
        for part in message.parts:
            if isinstance(part, TextPart):
                parts.append(part.text)
            elif hasattr(part, "data"):
                import json as _json
                parts.append(_json.dumps(part.data))
        return " ".join(parts)

