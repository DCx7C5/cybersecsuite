"""
Files API — upload forensic files once, reference by file_id in analyses.

Uses Anthropic's beta Files API (betas=["files-api-2025-04-14"]).
Analysts can upload PCAP, logs, memory dumps, PDFs once and re-use the
file_id across multiple agent queries without re-uploading.

Routes:
  POST   /v1/files                       — upload a file
  GET    /v1/files                       — list uploaded files
  GET    /v1/files/{file_id}             — get file metadata
  GET    /v1/files/{file_id}/download    — download file content
  DELETE /v1/files/{file_id}             — delete a file
"""


import logging
from typing import Any

import anthropic
from starlette.datastructures import UploadFile
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src.registries.providers import get_provider

logger = logging.getLogger("ai_proxy.files")

FILES_BETA = "files-api-2025-04-14"


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


async def upload_file(request: Request) -> JSONResponse:
    """
    POST /v1/files

    Accepts multipart/form-data with a 'file' field.
    Optional 'purpose' field (default: 'assistants').
    Returns file metadata including file_id for use in messages.
    """
    provider_id = request.headers.get("x-provider", "anthropic")
    client = _get_client(provider_id)
    if not client:
        return JSONResponse(
            {"error": {"message": f"Provider {provider_id!r} not configured", "type": "configuration_error"}},
            status_code=503,
        )

    try:
        form = await request.form()
    except Exception:
        return JSONResponse(
            {"error": {"message": "Expected multipart/form-data", "type": "invalid_request_error"}},
            status_code=400,
        )

    upload: UploadFile | None = form.get("file")  # type: ignore[assignment]
    if not upload or not isinstance(upload, UploadFile):
        return JSONResponse(
            {"error": {"message": "file field is required", "type": "invalid_request_error"}},
            status_code=400,
        )

    file_bytes = await upload.read()
    filename = upload.filename or "upload"

    try:
        result = await client.beta.files.upload(
            file=(filename, file_bytes, upload.content_type or "application/octet-stream"),
            betas=[FILES_BETA],
        )
        return JSONResponse(result.model_dump(), status_code=200)
    except anthropic.APIStatusError as exc:
        return JSONResponse(
            {"error": {"message": exc.message, "type": "upstream_error"}},
            status_code=exc.status_code,
        )
    finally:
        await client.close()


async def list_files(request: Request) -> JSONResponse:
    """GET /v1/files — list uploaded files."""
    provider_id = request.headers.get("x-provider", "anthropic")
    client = _get_client(provider_id)
    if not client:
        return JSONResponse(
            {"error": {"message": f"Provider {provider_id!r} not configured", "type": "configuration_error"}},
            status_code=503,
        )

    try:
        files: list[dict[str, Any]] = []
        async for f in client.beta.files.list(betas=[FILES_BETA]):
            files.append(f.model_dump())
        return JSONResponse({"data": files, "count": len(files)})
    except anthropic.APIStatusError as exc:
        return JSONResponse(
            {"error": {"message": exc.message, "type": "upstream_error"}},
            status_code=exc.status_code,
        )
    finally:
        await client.close()


async def get_file(request: Request) -> JSONResponse:
    """GET /v1/files/{file_id} — get file metadata."""
    file_id: str = request.path_params["file_id"]
    provider_id = request.headers.get("x-provider", "anthropic")
    client = _get_client(provider_id)
    if not client:
        return JSONResponse(
            {"error": {"message": f"Provider {provider_id!r} not configured", "type": "configuration_error"}},
            status_code=503,
        )

    try:
        f = await client.beta.files.retrieve_metadata(file_id, betas=[FILES_BETA])
        return JSONResponse(f.model_dump())
    except anthropic.NotFoundError:
        return JSONResponse({"error": {"message": f"File {file_id!r} not found"}}, status_code=404)
    except anthropic.APIStatusError as exc:
        return JSONResponse(
            {"error": {"message": exc.message, "type": "upstream_error"}},
            status_code=exc.status_code,
        )
    finally:
        await client.close()


async def delete_file(request: Request) -> JSONResponse:
    """DELETE /v1/files/{file_id} — delete a file."""
    file_id: str = request.path_params["file_id"]
    provider_id = request.headers.get("x-provider", "anthropic")
    client = _get_client(provider_id)
    if not client:
        return JSONResponse(
            {"error": {"message": f"Provider {provider_id!r} not configured", "type": "configuration_error"}},
            status_code=503,
        )

    try:
        await client.beta.files.delete(file_id, betas=[FILES_BETA])
        return JSONResponse({"deleted": True, "id": file_id})
    except anthropic.NotFoundError:
        return JSONResponse({"error": {"message": f"File {file_id!r} not found"}}, status_code=404)
    except anthropic.APIStatusError as exc:
        return JSONResponse(
            {"error": {"message": exc.message, "type": "upstream_error"}},
            status_code=exc.status_code,
        )
    finally:
        await client.close()


async def download_file(request: Request) -> Response:
    """GET /v1/files/{file_id}/download — stream raw file content."""
    file_id: str = request.path_params["file_id"]
    provider_id = request.headers.get("x-provider", "anthropic")
    client = _get_client(provider_id)
    if not client:
        return JSONResponse(
            {"error": {"message": f"Provider {provider_id!r} not configured", "type": "configuration_error"}},
            status_code=503,
        )

    try:
        raw = await client.beta.files.download(file_id, betas=[FILES_BETA])
        content = await raw.aread()
        # Use Content-Disposition so browser/clients know the filename
        return Response(
            content=content,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{file_id}"'},
        )
    except anthropic.NotFoundError:
        return JSONResponse({"error": {"message": f"File {file_id!r} not found"}}, status_code=404)
    except anthropic.APIStatusError as exc:
        return JSONResponse(
            {"error": {"message": exc.message, "type": "upstream_error"}},
            status_code=exc.status_code,
        )
    finally:
        await client.close()
