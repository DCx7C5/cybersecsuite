"""Workflow pipeline API: create, execute, and manage multi-step agent workflows."""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse

# ── In-memory workflow store ─────────────────────────────────────────────────

class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    id: str
    agent: str
    prompt: str
    depends_on: list[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    result: str | None = None
    error: str | None = None
    elapsed_ms: int = 0


@dataclass
class Workflow:
    id: str
    name: str
    steps: list[WorkflowStep]
    status: WorkflowStatus = WorkflowStatus.DRAFT
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["status"] = self.status.value
        d["steps"] = [
            {**asdict(s), "status": s.status.value}
            for s in self.steps
        ]
        return d


# Simple in-memory store (workflows are ephemeral — they run and complete)
_workflows: dict[str, Workflow] = {}


def _resolve_prompt(step: WorkflowStep, completed: dict[str, WorkflowStep]) -> str:
    """Inject dependency results into prompt via {{step_id}} placeholders."""
    prompt = step.prompt
    for dep_id in step.depends_on:
        dep = completed.get(dep_id)
        if dep and dep.result:
            # Replace {{dep_id}} with the result
            prompt = prompt.replace(f"{{{{{dep_id}}}}}", dep.result[:2000])
    return prompt


async def _run_step(step: WorkflowStep, completed: dict[str, WorkflowStep]) -> None:
    """Execute a single workflow step via the agent SDK."""
    step.status = StepStatus.RUNNING
    prompt = _resolve_prompt(step, completed)

    try:
        from a2a.agent_sdk import run_agent_query
        t0 = time.monotonic()
        result = await asyncio.wait_for(
            run_agent_query(agent_name=step.agent, prompt=prompt),
            timeout=180,
        )
        step.elapsed_ms = int((time.monotonic() - t0) * 1000)
        step.result = str(result) if result else ""
        step.status = StepStatus.COMPLETED
    except asyncio.TimeoutError:
        step.status = StepStatus.FAILED
        step.error = "timeout (180s)"
    except Exception as e:
        step.status = StepStatus.FAILED
        step.error = str(e)


async def _execute_workflow(workflow: Workflow) -> None:
    """Execute workflow steps respecting dependency order."""
    workflow.status = WorkflowStatus.RUNNING
    workflow.updated_at = time.time()

    completed: dict[str, WorkflowStep] = {}
    steps_by_id = {s.id: s for s in workflow.steps}

    # Topological execution: run steps whose dependencies are all complete
    remaining = set(steps_by_id.keys())

    while remaining:
        # Find runnable steps (all deps completed)
        runnable = []
        for sid in list(remaining):
            step = steps_by_id[sid]
            deps_met = all(
                dep_id in completed and completed[dep_id].status == StepStatus.COMPLETED
                for dep_id in step.depends_on
            )
            deps_failed = any(
                dep_id in completed and completed[dep_id].status == StepStatus.FAILED
                for dep_id in step.depends_on
            )
            if deps_failed:
                step.status = StepStatus.SKIPPED
                step.error = "dependency failed"
                completed[sid] = step
                remaining.discard(sid)
            elif deps_met:
                runnable.append(step)

        if not runnable:
            # Deadlock or all remaining skipped
            for sid in remaining:
                steps_by_id[sid].status = StepStatus.SKIPPED
                steps_by_id[sid].error = "deadlock: unresolvable dependencies"
            break

        # Run all runnable steps concurrently
        tasks = [_run_step(s, completed) for s in runnable]
        await asyncio.gather(*tasks, return_exceptions=True)

        for s in runnable:
            completed[s.id] = s
            remaining.discard(s.id)

    # Determine final workflow status
    statuses = {s.status for s in workflow.steps}
    if StepStatus.FAILED in statuses:
        workflow.status = WorkflowStatus.FAILED
    elif all(s.status == StepStatus.COMPLETED for s in workflow.steps):
        workflow.status = WorkflowStatus.COMPLETED
    else:
        workflow.status = WorkflowStatus.FAILED

    workflow.updated_at = time.time()


# ── Handlers ─────────────────────────────────────────────────────────────────

async def api_workflow_create(request: Request) -> JSONResponse:
    """POST /api/workflows — create and optionally execute a workflow.

    Body: {
        name: str,
        steps: [{id, agent, prompt, depends_on?: [str]}],
        execute?: bool  (default: true)
    }
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "invalid JSON body"}, status_code=400)

    name = body.get("name", "").strip()
    if not name:
        return JSONResponse({"error": "name is required"}, status_code=400)

    raw_steps = body.get("steps", [])
    if not raw_steps:
        return JSONResponse({"error": "at least one step is required"}, status_code=400)

    # Build workflow steps
    steps = []
    step_ids: set[str] = set()
    for i, raw in enumerate(raw_steps):
        sid = raw.get("id", f"step-{i+1}")
        if sid in step_ids:
            return JSONResponse({"error": f"duplicate step id: {sid}"}, status_code=400)
        step_ids.add(sid)

        agent = raw.get("agent", "").strip()
        if not agent:
            return JSONResponse({"error": f"step '{sid}' missing agent"}, status_code=400)

        prompt = raw.get("prompt", "").strip()
        if not prompt:
            return JSONResponse({"error": f"step '{sid}' missing prompt"}, status_code=400)

        deps = raw.get("depends_on", [])
        for dep in deps:
            if dep not in step_ids and dep not in {r.get("id", f"step-{j+1}") for j, r in enumerate(raw_steps)}:
                return JSONResponse({"error": f"step '{sid}' depends on unknown step '{dep}'"}, status_code=400)

        steps.append(WorkflowStep(
            id=sid,
            agent=agent,
            prompt=prompt,
            depends_on=deps,
        ))

    wf_id = str(uuid.uuid4())[:8]
    workflow = Workflow(id=wf_id, name=name, steps=steps)
    _workflows[wf_id] = workflow

    should_execute = body.get("execute", True)
    if should_execute:
        await _execute_workflow(workflow)

    return JSONResponse(workflow.to_dict(), status_code=201)


async def api_workflow_list(request: Request) -> JSONResponse:
    """GET /api/workflows — list all workflows."""
    workflows = [wf.to_dict() for wf in _workflows.values()]
    return JSONResponse({"total": len(workflows), "workflows": workflows})


async def api_workflow_get(request: Request) -> JSONResponse:
    """GET /api/workflows/{id} — get workflow details."""
    wf_id = request.path_params.get("id", "")
    wf = _workflows.get(wf_id)
    if not wf:
        return JSONResponse({"error": f"workflow '{wf_id}' not found"}, status_code=404)
    return JSONResponse(wf.to_dict())


async def api_workflow_cancel(request: Request) -> JSONResponse:
    """DELETE /api/workflows/{id} — cancel/delete a workflow."""
    wf_id = request.path_params.get("id", "")
    wf = _workflows.pop(wf_id, None)
    if not wf:
        return JSONResponse({"error": f"workflow '{wf_id}' not found"}, status_code=404)
    return JSONResponse({"status": "deleted", "workflow": wf_id})


async def api_workflow_update(request: Request) -> JSONResponse:
    """PATCH /api/workflows/{id} — update workflow metadata or step status."""
    wf_id = request.path_params.get("id", "")
    wf = _workflows.get(wf_id)
    if not wf:
        return JSONResponse({"error": f"workflow '{wf_id}' not found"}, status_code=404)
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "invalid JSON body"}, status_code=400)
    # Patch top-level scalar fields stored in the internal dict
    d = wf.to_dict()
    for field in ("status", "current_step", "metadata"):
        if field in body:
            d[field] = body[field]
    # Reflect back into the WorkflowRun object where possible
    if hasattr(wf, "status") and "status" in body:
        wf.status = body["status"]
    return JSONResponse({"ok": True, "workflow": wf_id})
