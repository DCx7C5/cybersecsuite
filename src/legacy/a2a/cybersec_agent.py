"""
Cybersecurity A2A Agent — concrete implementation wired to the cybersecsuite.
Handles cybersecurity tasks: CVE lookup, IOC analysis, MITRE ATT&CK, artifacts.
Fully integrated with db ORM models and crypto signing.
"""


from typing import Any, Optional
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
        version="0.1.0",
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
                await self._handle_generic(task, text)
        except Exception as e:
            self._fail(task.id, f"Agent error: {e}")

        # Persist task to DB after execution
        await self.store.persist_task(
            self.store.get(task.id) or task
        )

    # ── Skill Handlers ────────────────────────────────────────────────────────

    async def _handle_cve(self, task: Task, text: str) -> None:
        """CVE lookup skill — queries DB for context, then uses AI for analysis."""
        import re
        from a2a.agent_sdk import run_agent_query
        from db.models.cve import CVEIntel as CVEEntry

        cve_pattern = re.compile(r"cve-\d{4}-\d{4,}", re.IGNORECASE)
        match = cve_pattern.search(text)

        db_context: list[dict] = []
        if match:
            cve_id = match.group(0).upper()
            entry = await CVEEntry.get_or_none(cve_id=cve_id)
            if entry:
                db_context.append({
                    "cve_id": entry.cve_id,
                    "description": entry.description,
                    "cvss_score": float(entry.cvss_score) if hasattr(entry, "cvss_score") and entry.cvss_score else None,
                    "severity": entry.severity if hasattr(entry, "severity") else None,
                    "published": entry.published_at.isoformat() if hasattr(entry, "published_at") and entry.published_at else None,
                })
        else:
            entries = await CVEEntry.all().order_by("-created_at").limit(5)
            for entry in entries:
                db_context.append({"cve_id": entry.cve_id, "description": getattr(entry, "description", "")})

        context_str = f"DB context: {db_context}\n\n" if db_context else ""
        session_out: dict[str, Any] = {}
        ai_result = await run_agent_query(
            "cybersec-analyst",
            f"{context_str}Analyze and provide threat intelligence for: {text}",
            session_id=task.session_id,
            _session_out=session_out,
        )
        if session_out.get("session_id"):
            task.session_id = session_out["session_id"]
        result_text = ai_result or f"CVE lookup complete. Found {len(db_context)} local result(s)."

        self.store.add_artifact(task.id, TaskArtifact(
            name="cve-result",
            parts=[DataPart(type=PartType.DATA, data={"cves": db_context, "analysis": result_text, "query": text})],
        ))
        self._reply(task.id, result_text)

    async def _handle_ioc(self, task: Task, text: str) -> None:
        """IOC analysis skill — queries DB for IOC context, then uses AI for enrichment."""
        from a2a.agent_sdk import run_agent_query
        from db.models.investigation import IOC

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
            for ioc in iocs[:5]:
                matches.append({
                    "ioc_id": ioc.ioc_id,
                    "type": ioc.ioc_type,
                    "value": ioc.value,
                    "confidence": ioc.confidence.value if ioc.confidence else None,
                    "status": ioc.status.value if ioc.status else None,
                })

        context_str = f"Known IOCs from DB: {matches}\n\n" if matches else ""
        session_out: dict[str, Any] = {}
        ai_result = await run_agent_query(
            "cybersec-analyst",
            f"{context_str}Analyze these indicators and provide threat intelligence: {text}",
            session_id=task.session_id,
            _session_out=session_out,
        )
        if session_out.get("session_id"):
            task.session_id = session_out["session_id"]
        result_text = ai_result or f"IOC analysis complete. Found {len(matches)} indicator(s)."

        self.store.add_artifact(task.id, TaskArtifact(
            name="ioc-result",
            parts=[DataPart(type=PartType.DATA, data={"iocs": matches, "analysis": result_text, "query": text})],
        ))
        self._reply(task.id, result_text)

    async def _handle_mitre(self, task: Task, text: str) -> None:
        """MITRE ATT&CK skill — queries DB then uses AI for technique analysis."""
        import re
        from a2a.agent_sdk import run_agent_query
        from db.models.investigation import MITRETechnique

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
            techniques = await MITRETechnique.all().order_by("technique_id").limit(10)
            for t in techniques:
                if any(kw in (t.name or "").lower() or kw in (t.description or "").lower()
                       for kw in text.split() if len(kw) > 3):
                    results.append({
                        "technique_id": t.technique_id,
                        "name": t.name,
                        "tactic": t.tactic,
                    })

        context_str = f"DB MITRE techniques: {results}\n\n" if results else ""
        session_out: dict[str, Any] = {}
        ai_result = await run_agent_query(
            "cybersec-analyst",
            f"{context_str}Provide MITRE ATT&CK analysis and detection guidance for: {text}",
            session_id=task.session_id,
            _session_out=session_out,
        )
        if session_out.get("session_id"):
            task.session_id = session_out["session_id"]
        result_text = ai_result or f"MITRE ATT&CK lookup complete. Found {len(results)} technique(s)."

        self.store.add_artifact(task.id, TaskArtifact(
            name="mitre-result",
            parts=[DataPart(type=PartType.DATA, data={"techniques": results, "analysis": result_text, "query": text})],
        ))
        self._reply(task.id, result_text)

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
                name=f"google_a2a-task-{task.id[:8]}",
                content=payload,
                description=f"Signed via A2A task {task.id}",
                created_by="google_a2a-agent",
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
        """Threat modeling skill — gathers DB context then uses AI for threat modeling."""
        from a2a.agent_sdk import run_agent_query
        from db.models.investigation import Finding, Risk

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

        context_str = f"Active findings: {findings_data}\nActive risks: {risks_data}\n\n"
        session_out: dict[str, Any] = {}
        ai_result = await run_agent_query(
            "threat-modeler",
            f"{context_str}Generate a threat model and attack surface analysis for: {text}",
            session_id=task.session_id,
            _session_out=session_out,
        )
        if session_out.get("session_id"):
            task.session_id = session_out["session_id"]
        result_text = ai_result or f"Threat model complete. {len(findings_data)} findings, {len(risks_data)} risks in context."

        self.store.add_artifact(task.id, TaskArtifact(
            name="threat-model",
            parts=[DataPart(type=PartType.DATA, data={
                "query": text,
                "analysis": result_text,
                "active_findings": findings_data,
                "active_risks": risks_data,
                "finding_count": len(findings_data),
                "risk_count": len(risks_data),
            })],
        ))
        self._reply(task.id, result_text)

    async def _handle_generic(self, task: Task, text: str) -> None:
        """Generic fallback — routes unrecognised tasks to the cybersec-analyst via SDK.

        The SDK loads .claude/agents/cybersec-analyst.md and uses its declared model
        (routed through the AI asgi) to respond. Session continuity is preserved.
        """
        from a2a.agent_sdk import run_agent_query
        session_out: dict[str, Any] = {}
        result = await run_agent_query(
            "cybersec-analyst",
            text,
            session_id=task.session_id,
            _session_out=session_out,
        )
        if session_out.get("session_id"):
            task.session_id = session_out["session_id"]
        self._reply(task.id, result or "No response from agent.")

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_text(message: Message) -> str:
        """Extract plain text from message parts (including DataPart JSON)."""
        parts = []
        for part in message.parts:
            if isinstance(part, TextPart):
                parts.append(part.text)
            elif hasattr(part, "data"):
                import json as _json
                parts.append(_json.dumps(part.data))
        return " ".join(parts)

