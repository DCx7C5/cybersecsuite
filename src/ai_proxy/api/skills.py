"""
Skills API — manage Anthropic beta skills (knowledge packages for models).

Skills let Claude learn from uploaded file collections, enabling domain-specific
expertise for forensic analysis, threat intelligence, CVE research, etc.

Routes:
  POST   /v1/beta/skills                                   — create a skill
  GET    /v1/beta/skills                                   — list skills
  GET    /v1/beta/skills/{skill_id}                        — retrieve a skill
  DELETE /v1/beta/skills/{skill_id}                        — delete a skill
  GET    /v1/beta/skills/{skill_id}/versions               — list skill versions
  GET    /v1/beta/skills/{skill_id}/versions/{version_id}  — retrieve a specific version
"""


import logging
from typing import Any

import anthropic
from starlette.datastructures import UploadFile
from starlette.requests import Request
from starlette.responses import JSONResponse

from ai_proxy.providers.registry import get_provider

logger = logging.getLogger("ai_proxy.skills")

SKILLS_BETA = "skills-2025-05-15"


def _get_client(provider_id: str = "anthropic") -> anthropic.AsyncAnthropic | None:
    provider = get_provider(provider_id)
    if not provider:
        return None
    api_key = provider.get_api_key()
    if not api_key:
        return None
    return anthropic.AsyncAnthropic(
        api_key=api_key,
        base_url=provider.base_url,
        max_retries=2,
    )


async def create_skill(request: Request) -> JSONResponse:
    """
    POST /v1/beta/skills

    Body (multipart/form-data OR JSON):
    - display_title: optional string
    - files: one or more files (multipart only)

    Returns skill object with skill_id for use in messages.
    """
    provider_id = request.headers.get("x-provider", "anthropic")
    client = _get_client(provider_id)
    if not client:
        return JSONResponse(
            {"error": {"message": f"Provider {provider_id!r} not configured", "type": "configuration_error"}},
            status_code=503,
        )

    try:
        content_type = request.headers.get("content-type", "")
        if "multipart/form-data" in content_type:
            form = await request.form()
            display_title: str | None = form.get("display_title")  # type: ignore[assignment]
            files_raw = form.getlist("files")
            file_list = []
            for f in files_raw:
                if isinstance(f, UploadFile):
                    data = await f.read()
                    file_list.append((f.filename or "file", data, f.content_type or "application/octet-stream"))
        else:
            body = await request.json()
            display_title = body.get("display_title")
            file_list = None  # no files from JSON body

        kwargs: dict[str, Any] = {"betas": [SKILLS_BETA]}
        if display_title:
            kwargs["display_title"] = display_title
        if file_list:
            kwargs["files"] = file_list

        skill = await client.beta.skills.create(**kwargs)
        return JSONResponse(skill.model_dump(), status_code=200)
    except anthropic.APIStatusError as exc:
        return JSONResponse(
            {"error": {"message": exc.message, "type": "upstream_error"}},
            status_code=exc.status_code,
        )
    finally:
        await client.close()


async def list_skills(request: Request) -> JSONResponse:
    """GET /v1/beta/skills — list all skills."""
    provider_id = request.headers.get("x-provider", "anthropic")
    client = _get_client(provider_id)
    if not client:
        return JSONResponse(
            {"error": {"message": f"Provider {provider_id!r} not configured", "type": "configuration_error"}},
            status_code=503,
        )

    try:
        limit = int(request.query_params.get("limit", 20))
        page = request.query_params.get("page")
        source = request.query_params.get("source")

        kwargs: dict[str, Any] = {"betas": [SKILLS_BETA], "limit": limit}
        if page:
            kwargs["page"] = page
        if source:
            kwargs["source"] = source

        skills: list[dict[str, Any]] = []
        async for s in client.beta.skills.list(**kwargs):
            skills.append(s.model_dump())
        return JSONResponse({"data": skills, "count": len(skills)})
    except anthropic.APIStatusError as exc:
        return JSONResponse(
            {"error": {"message": exc.message, "type": "upstream_error"}},
            status_code=exc.status_code,
        )
    finally:
        await client.close()


async def get_skill(request: Request) -> JSONResponse:
    """GET /v1/beta/skills/{skill_id} — retrieve a skill."""
    skill_id: str = request.path_params["skill_id"]
    provider_id = request.headers.get("x-provider", "anthropic")
    client = _get_client(provider_id)
    if not client:
        return JSONResponse(
            {"error": {"message": f"Provider {provider_id!r} not configured", "type": "configuration_error"}},
            status_code=503,
        )

    try:
        skill = await client.beta.skills.retrieve(skill_id, betas=[SKILLS_BETA])
        return JSONResponse(skill.model_dump())
    except anthropic.NotFoundError:
        return JSONResponse({"error": {"message": f"Skill {skill_id!r} not found"}}, status_code=404)
    except anthropic.APIStatusError as exc:
        return JSONResponse(
            {"error": {"message": exc.message, "type": "upstream_error"}},
            status_code=exc.status_code,
        )
    finally:
        await client.close()


async def delete_skill(request: Request) -> JSONResponse:
    """DELETE /v1/beta/skills/{skill_id} — delete a skill."""
    skill_id: str = request.path_params["skill_id"]
    provider_id = request.headers.get("x-provider", "anthropic")
    client = _get_client(provider_id)
    if not client:
        return JSONResponse(
            {"error": {"message": f"Provider {provider_id!r} not configured", "type": "configuration_error"}},
            status_code=503,
        )

    try:
        result = await client.beta.skills.delete(skill_id, betas=[SKILLS_BETA])
        return JSONResponse(result.model_dump())
    except anthropic.NotFoundError:
        return JSONResponse({"error": {"message": f"Skill {skill_id!r} not found"}}, status_code=404)
    except anthropic.APIStatusError as exc:
        return JSONResponse(
            {"error": {"message": exc.message, "type": "upstream_error"}},
            status_code=exc.status_code,
        )
    finally:
        await client.close()


async def list_skill_versions(request: Request) -> JSONResponse:
    """GET /v1/beta/skills/{skill_id}/versions — list all versions of a skill."""
    skill_id: str = request.path_params["skill_id"]
    provider_id = request.headers.get("x-provider", "anthropic")
    client = _get_client(provider_id)
    if not client:
        return JSONResponse(
            {"error": {"message": f"Provider {provider_id!r} not configured", "type": "configuration_error"}},
            status_code=503,
        )

    try:
        versions: list[dict[str, Any]] = []
        async for v in client.beta.skills.versions.list(skill_id, betas=[SKILLS_BETA]):
            versions.append(v.model_dump())
        return JSONResponse({"skill_id": skill_id, "data": versions, "count": len(versions)})
    except anthropic.NotFoundError:
        return JSONResponse({"error": {"message": f"Skill {skill_id!r} not found"}}, status_code=404)
    except anthropic.APIStatusError as exc:
        return JSONResponse(
            {"error": {"message": exc.message, "type": "upstream_error"}},
            status_code=exc.status_code,
        )
    finally:
        await client.close()


async def get_skill_version(request: Request) -> JSONResponse:
    """GET /v1/beta/skills/{skill_id}/versions/{version_id} — retrieve a specific skill version."""
    skill_id: str = request.path_params["skill_id"]
    version_id: str = request.path_params["version_id"]
    provider_id = request.headers.get("x-provider", "anthropic")
    client = _get_client(provider_id)
    if not client:
        return JSONResponse(
            {"error": {"message": f"Provider {provider_id!r} not configured", "type": "configuration_error"}},
            status_code=503,
        )

    try:
        version = await client.beta.skills.versions.retrieve(skill_id, version_id, betas=[SKILLS_BETA])
        return JSONResponse(version.model_dump())
    except anthropic.NotFoundError:
        return JSONResponse(
            {"error": {"message": f"Skill {skill_id!r} version {version_id!r} not found"}},
            status_code=404,
        )
    except anthropic.APIStatusError as exc:
        return JSONResponse(
            {"error": {"message": exc.message, "type": "upstream_error"}},
            status_code=exc.status_code,
        )
    finally:
        await client.close()
