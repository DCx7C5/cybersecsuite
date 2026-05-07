"""Planner orchestrator glue for proposal, analysis, and step tracking."""

from __future__ import annotations

from datetime import datetime

from css.modules.working_dir import WorkingDirectoryManager

from .analyzer import ArchitectureAnalyzer
from .decision_log import DecisionLog
from .models import PlanStep, PlanStepStatus, PlannerSession
from .store import ProposalStore


class PlannerOrchestrator:
    """Creates and updates planner sessions in development mode."""

    def __init__(
        self,
        proposal_store: ProposalStore | None = None,
        analyzer: ArchitectureAnalyzer | None = None,
        decision_log: DecisionLog | None = None,
        working_dirs: WorkingDirectoryManager | None = None,
    ):
        self.proposal_store = proposal_store or ProposalStore()
        self.analyzer = analyzer or ArchitectureAnalyzer()
        self.decision_log = decision_log or DecisionLog()
        self.working_dirs = working_dirs or WorkingDirectoryManager()

    def create_session(self, session_id: str, agent_id: str, objective: str, steps: list[str]) -> PlannerSession:
        self.working_dirs.create(session_id=session_id, agent_id=agent_id, mode="planner")
        plan = PlannerSession(
            session_id=session_id,
            objective=objective,
            steps=[
                PlanStep(step_id=f"step-{i+1}", description=description)
                for i, description in enumerate(steps)
            ],
        )
        self.proposal_store.write(plan)
        self.decision_log.append(
            session_id=session_id,
            decision="plan_created",
            metadata={"objective": objective, "step_count": len(steps), "architecture": self.analyzer.summarize()},
        )
        return plan

    def mark_step(self, plan: PlannerSession, step_id: str, status: PlanStepStatus, result: str = "") -> PlannerSession:
        updated = False
        for step in plan.steps:
            if step.step_id == step_id:
                step.status = status
                step.result = result
                updated = True
                break
        if not updated:
            raise ValueError(f"Step not found: {step_id}")

        plan.updated_at = datetime.utcnow()
        self.proposal_store.write(plan)
        self.decision_log.append(
            session_id=plan.session_id,
            decision="step_updated",
            metadata={"step_id": step_id, "status": status.value},
        )
        return plan
