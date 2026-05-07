"""Report generation endpoints."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from .generator import ReportGenerator
from .models import ReportRecord

router = APIRouter(prefix="/api/reports", tags=["reports"])
generator = ReportGenerator()


class ReportSection(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: Any = ""


class GenerateReportRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    report_type: str = Field(..., pattern="^(markdown|html|pdf)$")
    source_type: str = Field("incident", min_length=1, max_length=32)
    source_id: str = Field(..., min_length=1, max_length=128)
    sections: list[ReportSection] = Field(default_factory=list)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def generate_report(req: GenerateReportRequest, org_id: int = Query(..., description="Organization ID")) -> dict:
    report_id = f"REP-{uuid.uuid4().hex[:16]}"
    sections = [s.model_dump() for s in req.sections]

    if req.report_type == "markdown":
        content = generator.render_markdown(req.title, sections)
    elif req.report_type == "html":
        content = generator.render_html(req.title, sections)
    else:
        content = generator.render_pdf(req.title, sections).decode("utf-8")

    record = await ReportRecord.create(
        organization_id=org_id,
        report_id=report_id,
        title=req.title,
        report_type=req.report_type,
        source_type=req.source_type,
        source_id=req.source_id,
        content=content,
    )
    return {"report_id": record.report_id, "report_type": record.report_type, "status": "generated"}


@router.get("/")
async def list_reports(
    org_id: int = Query(..., description="Organization ID"),
    source_type: str | None = None,
    source_id: str | None = None,
    limit: int = Query(50, ge=1, le=500),
) -> list[dict]:
    query = ReportRecord.filter(organization_id=org_id)
    if source_type:
        query = query.filter(source_type=source_type)
    if source_id:
        query = query.filter(source_id=source_id)
    reports = await query.order_by("-generated_at").limit(limit).all()
    return [
        {
            "report_id": report.report_id,
            "title": report.title,
            "report_type": report.report_type,
            "source_type": report.source_type,
            "source_id": report.source_id,
            "generated_at": report.generated_at.isoformat(),
        }
        for report in reports
    ]


@router.get("/{report_id}")
async def get_report(report_id: str, org_id: int = Query(..., description="Organization ID")) -> dict:
    report = await ReportRecord.get_or_none(organization_id=org_id, report_id=report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {
        "report_id": report.report_id,
        "title": report.title,
        "report_type": report.report_type,
        "source_type": report.source_type,
        "source_id": report.source_id,
        "content": report.content,
        "generated_at": report.generated_at.isoformat(),
    }
