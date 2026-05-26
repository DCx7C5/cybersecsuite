# @reports - Findings Aggregation and Report Delivery

**Location**: `src/css/modules/reports/`
**Phase ownership**: Phase 32 - Reports Module
**Status**: Partial runtime exists; target pipeline remains to be reconciled and implemented.

## Purpose

Turn incident, scan, compliance, and session findings into deliverables:

- collect source facts into a typed report context
- render Markdown and HTML artifacts from maintained templates
- export PDF and JSON artifacts
- expose generation status, artifact download, and template management APIs
- emit lifecycle events for UI updates and audit trails

This is the executable implementation specification for the reports area. Global
status belongs in `.plan/session.db`; the documentation sanitization pass does
not mutate that tracker.

## Current Code Reality

| File | Current behavior | Gap against Phase 32 |
|------|------------------|----------------------|
| `models.py` | `ReportRecord` persists title, raw `report_type`, source reference, and content in one table. | No report status, artifact model, template model, or enum-owned fields. |
| `generator.py` | `ReportGenerator` renders Markdown/HTML synchronously; PDF is UTF-8 Markdown bytes. | No template renderer, actual PDF export, checksum, or JSON artifact pipeline. |
| `endpoints.py` | `POST /api/reports/` renders and saves inline, returning HTTP 201; list/get endpoints exist. | Target is asynchronous HTTP 202 generation with status/artifact/download/template endpoints. |

Implemented symbol map:

| File | Existing symbols to preserve or migrate deliberately |
|------|-----------------------------------------------|
| `models.py` | `ReportRecord` |
| `generator.py` | `ReportGenerator` |
| `endpoints.py` | `ReportSection`, `GenerateReportRequest`, `generate_report`, `list_reports`, `get_report` |

The existing endpoint is a useful scaffold, not evidence that Phase 32 is
complete. Do not delete or rewrite it solely from this plan; audit migration
steps against callers and stored rows first.

## Target Domain Model

### Enums

| Enum | Required values |
|------|-----------------|
| `ReportType` | `INCIDENT`, `SCAN`, `COMPLIANCE`, `SESSION`, `EXECUTIVE` |
| `ReportFormat` | `MARKDOWN`, `HTML`, `PDF`, `JSON` |
| `ReportStatus` | `PENDING`, `GENERATING`, `READY`, `FAILED` |

### Persistence

| Model | Required responsibility |
|-------|-------------------------|
| `Report` | Generation request, source references, requested formats, lifecycle status, failure reason, requesting organization/user. |
| `ReportArtifact` | One produced format per report, inline content or durable path, MIME type, byte size, SHA-256 digest. |
| `ReportTemplate` | Named editable template per report type/format with built-in marker and active/version metadata. |

Use repository-standard Tortoise ORM entities and shared enum ownership after
the database-model consolidation contract is confirmed. Preserve organization
scoping from the existing runtime.

## Generation Pipeline

```text
POST /api/reports/
  -> create Report(status=PENDING)
  -> enqueue generation work
  -> return 202 with report id

worker/report service
  -> status=GENERATING
  -> ReportBuilder.build(report) gathers source data
  -> ReportRenderer renders requested Markdown/HTML artifacts
  -> ReportExporter produces PDF/JSON artifacts when requested
  -> persist ReportArtifact rows and status=READY
  -> emit report.generated

failure
  -> persist status=FAILED and error_message
  -> emit report.generation.failed
```

| Service | Contract |
|---------|----------|
| `ReportBuilder` | `async build(report) -> ReportContext`; query source modules by explicit references and return normalized sections/findings/evidence/metadata. |
| `ReportRenderer` | Render Markdown using templates; derive safe HTML from rendered content; store string artifacts. |
| `ReportExporter` | Export PDF from HTML into configured artifacts storage and JSON from context; persist digest and output metadata. |

## Built-In Templates

Seed and protect five built-in templates while permitting user-maintained
copies or overrides:

| Template | Primary audience/content |
|----------|--------------------------|
| Incident response | Timeline, impact, evidence, actions, remediation. |
| Scan findings | Scope, vulnerabilities, severities, technical recommendations. |
| Compliance assessment | Control coverage, failures, evidence links, remediation. |
| Session summary | Objectives, activities, tool actions, conclusions. |
| Executive summary | Concise risk, business impact, priorities, next decisions. |

## API Contract

| Method | Route | Required result |
|--------|-------|-----------------|
| `POST` | `/api/reports/` | Create queued report; HTTP 202 and report identifier. |
| `GET` | `/api/reports/` | Filtered list with type/status/source/date fields. |
| `GET` | `/api/reports/{id}` | Report metadata, lifecycle status, artifacts, and error state. |
| `GET` | `/api/reports/{id}/artifacts/{artifact_id}` | Download or serve the requested artifact safely. |
| `GET` | `/api/reports/templates/` | List built-in and editable templates. |
| `POST` | `/api/reports/templates/` | Create an editable template. |
| `PUT` | `/api/reports/templates/{id}` | Update a non-protected template. |

## Integrations

| Area | Relationship |
|------|--------------|
| `modules/incidents`, `modules/scans`, `modules/compliance` | Primary structured report inputs. |
| `modules/sessions` | Session summary input once session ownership is reconciled. |
| `core/auth` / organization scope | Restrict report generation, lookup, and downloads. |
| `core/events` | Emit queued/generated/failed lifecycle events. |
| `core/templates` | Own frontend `ReportsPanel`, `GenerateReportModal`, `ReportViewer`, and template editor surfaces. |

## Execution Order

| Todo ID | Work | Preconditions |
|---------|------|---------------|
| `reports-enums` | Add report enums in canonical database enum location. | Database enum ownership confirmed. |
| `reports-orm` | Add `Report`, `ReportArtifact`, and `ReportTemplate` ORM surfaces and registration. | `reports-enums`, database initialization contract. |
| `reports-builder` | Build normalized contexts from domain modules. | ORM and source-module APIs available. |
| `reports-renderer` | Implement maintained Markdown/HTML rendering. | Builder and seeded templates. |
| `reports-pdf-export` | Create real PDF artifact with digest. | Renderer and artifacts storage. |
| `reports-json-export` | Create JSON context artifact. | Renderer/builder. |
| `reports-template-seeds` | Seed five built-in templates idempotently. | Template model. |
| `reports-background-generation` | Execute lifecycle outside request path and record failures. | Builder/render/export services. |
| `reports-endpoints` | Replace scaffold routes with queued/status/artifact/template contract. | Services and authorization. |
| `reports-events` | Emit lifecycle events. | Event runtime and background flow. |
| `reports-frontend` | Add reports UI panels and viewer. | Endpoints stable. |

## Local Rules

- Module-owned implementation detail stays in this document, not in the
  global plan index.
- ORM models inherit `css.core.db.models.base.BaseModel`.
- Confirm enum ownership against the database consolidation work before adding
  duplicate module enums.
- Keep generated artifacts out of source directories and protect downloads by
  organization/user authorization.
