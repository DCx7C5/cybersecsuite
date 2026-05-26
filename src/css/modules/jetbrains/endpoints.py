from fastapi import APIRouter, Query

from .client import PyCharmToolClient
from .database import DatabaseClient
from .types import FileLocation, RunConfiguration, SearchQuery

router = APIRouter(prefix="/api/ide", tags=["jetbrains"])

_client: PyCharmToolClient | None = None
_db_client: DatabaseClient | None = None


def init_clients(client: PyCharmToolClient, db_client: DatabaseClient) -> None:
    global _client, _db_client
    _client = client
    _db_client = db_client


# ── Status ───────────────────────────────────────────────────────────


@router.get("/status")
async def get_status() -> dict:
    if _client is None or _db_client is None:
        return {"available": False, "client": False, "database": False}
    return {
        "available": _client.is_available,
        "client": _client.is_available,
        "database": _db_client.is_available,
    }


# ── File operations ──────────────────────────────────────────────────


@router.get("/files/read")
async def read_file(path: str = Query(...)) -> dict:
    if _client is None:
        return {"success": False, "error": "IDE client not initialized"}
    result = await _client.read_file(path)
    return {"success": result.success, "data": result.data, "error": result.error}


@router.post("/files/create")
async def create_file(path: str = Query(...), content: str = "") -> dict:
    if _client is None:
        return {"success": False, "error": "IDE client not initialized"}
    result = await _client.create_file(path, content)
    return {"success": result.success, "error": result.error}


@router.post("/files/replace")
async def replace_text(
    path: str = Query(...),
    old_text: str = Query(...),
    new_text: str = Query(...),
    replace_all: bool = True,
    case_sensitive: bool = True,
    regex: bool = False,
) -> dict:
    if _client is None:
        return {"success": False, "error": "IDE client not initialized"}
    result = await _client.replace_text(path, old_text, new_text, replace_all, case_sensitive, regex)
    return {"success": result.success, "data": result.data, "error": result.error}


@router.post("/files/open")
async def open_file(path: str = Query(...), line: int | None = Query(None), column: int | None = Query(None)) -> dict:
    if _client is None:
        return {"success": False, "error": "IDE client not initialized"}
    result = await _client.open_file(FileLocation(path=path, line=line, column=column))
    return {"success": result.success, "error": result.error}


@router.post("/files/reformat")
async def reformat_file(path: str = Query(...)) -> dict:
    if _client is None:
        return {"success": False, "error": "IDE client not initialized"}
    result = await _client.reformat_file(path)
    return {"success": result.success, "error": result.error}


# ── Search ────────────────────────────────────────────────────────────


@router.get("/search/text")
async def search_text(
    pattern: str = Query(...),
    case_sensitive: bool = True,
    file_mask: str | None = Query(None),
    max_results: int = 50,
) -> dict:
    if _client is None:
        return {"success": False, "error": "IDE client not initialized"}
    query = SearchQuery(pattern=pattern, mode="text", case_sensitive=case_sensitive, file_mask=file_mask, max_results=max_results)
    result = await _client.search_text(query)
    return {"success": result.success, "data": result.data, "error": result.error}


@router.get("/search/regex")
async def search_regex(
    pattern: str = Query(...),
    case_sensitive: bool = True,
    file_mask: str | None = Query(None),
    max_results: int = 50,
) -> dict:
    if _client is None:
        return {"success": False, "error": "IDE client not initialized"}
    query = SearchQuery(pattern=pattern, mode="regex", case_sensitive=case_sensitive, file_mask=file_mask, max_results=max_results)
    result = await _client.search_regex(query)
    return {"success": result.success, "data": result.data, "error": result.error}


@router.get("/search/symbol")
async def search_symbol(name: str = Query(...)) -> dict:
    if _client is None:
        return {"success": False, "error": "IDE client not initialized"}
    result = await _client.search_symbol(name)
    return {"success": result.success, "data": result.data, "error": result.error}


@router.get("/search/files")
async def find_files(pattern: str = Query(...), by_name: bool = False) -> dict:
    if _client is None:
        return {"success": False, "error": "IDE client not initialized"}
    result = await _client.find_files_by_glob(pattern) if not by_name else await _client.find_files_by_name(pattern)
    return {"success": result.success, "data": result.data, "error": result.error}


# ── Code analysis ────────────────────────────────────────────────────


@router.get("/analysis/problems")
async def get_file_problems(path: str = Query(...)) -> dict:
    if _client is None:
        return {"success": False, "error": "IDE client not initialized"}
    result = await _client.get_file_problems(path)
    return {"success": result.success, "data": result.data, "error": result.error}


@router.get("/analysis/symbol-info")
async def get_symbol_info(path: str = Query(...), line: int = Query(...), column: int = Query(...)) -> dict:
    if _client is None:
        return {"success": False, "error": "IDE client not initialized"}
    result = await _client.get_symbol_info(path, line, column)
    return {"success": result.success, "data": result.data, "error": result.error}


@router.post("/analysis/build")
async def build_project() -> dict:
    if _client is None:
        return {"success": False, "error": "IDE client not initialized"}
    result = await _client.build_project()
    return {"success": result.success, "data": result.data, "error": result.error}


# ── Run ──────────────────────────────────────────────────────────────


@router.get("/run/configurations")
async def list_run_configurations() -> dict:
    if _client is None:
        return {"success": False, "error": "IDE client not initialized"}
    result = await _client.list_run_configurations()
    return {"success": result.success, "data": result.data, "error": result.error}


@router.post("/run/execute")
async def execute_run_configuration(
    name: str = Query(...),
    program_arguments: str | None = Query(None),
    working_directory: str | None = Query(None),
) -> dict:
    if _client is None:
        return {"success": False, "error": "IDE client not initialized"}
    config = RunConfiguration(name=name, program_arguments=program_arguments, working_directory=working_directory)
    result = await _client.execute_run_configuration(config)
    return {"success": result.success, "data": result.data, "error": result.error}


# ── Refactoring ──────────────────────────────────────────────────────


@router.post("/refactor/rename")
async def rename_symbol(path: str = Query(...), old_name: str = Query(...), new_name: str = Query(...)) -> dict:
    if _client is None:
        return {"success": False, "error": "IDE client not initialized"}
    result = await _client.rename_symbol(path, old_name, new_name)
    return {"success": result.success, "error": result.error}


# ── Project info ─────────────────────────────────────────────────────


@router.get("/project/info")
async def get_project_info() -> dict:
    if _client is None:
        return {"success": False, "error": "IDE client not initialized"}
    result = await _client.get_project_info()
    return {"success": result.success, "data": result.data, "error": result.error}


@router.get("/project/tree")
async def list_directory(path: str = Query("."), max_depth: int = Query(3)) -> dict:
    if _client is None:
        return {"success": False, "error": "IDE client not initialized"}
    result = await _client.list_directory_tree(path, max_depth)
    return {"success": result.success, "data": result.data, "error": result.error}


# ── Database operations ──────────────────────────────────────────────


@router.get("/database/connections")
async def list_database_connections() -> dict:
    if _db_client is None:
        return {"success": False, "error": "Database client not initialized"}
    result = await _db_client.list_connections()
    return {"success": result.success, "data": result.data, "error": result.error}


@router.get("/database/schemas")
async def list_schemas(connection_id: str = Query(...)) -> dict:
    if _db_client is None:
        return {"success": False, "error": "Database client not initialized"}
    result = await _db_client.list_schemas(connection_id)
    return {"success": result.success, "data": result.data, "error": result.error}


@router.get("/database/objects")
async def list_objects(
    connection_id: str = Query(...),
    database_name: str = Query(...),
    schema_name: str = Query(...),
    kind: str | None = Query(None),
) -> dict:
    if _db_client is None:
        return {"success": False, "error": "Database client not initialized"}
    result = await _db_client.list_schema_objects(connection_id, database_name, schema_name, kind)
    return {"success": result.success, "data": result.data, "error": result.error}


@router.post("/database/query")
async def execute_query(
    connection_id: str = Query(...),
    database_name: str = Query(...),
    schema_name: str = Query(...),
    query_text: str = Query(...),
) -> dict:
    if _db_client is None:
        return {"success": False, "error": "Database client not initialized"}
    result = await _db_client.execute_query(connection_id, database_name, schema_name, query_text)
    return {"success": result.success, "data": result.data, "error": result.error}


@router.get("/database/preview")
async def preview_table(
    connection_id: str = Query(...),
    database_name: str = Query(...),
    schema_name: str = Query(...),
    table_name: str = Query(...),
    max_rows: int = 100,
) -> dict:
    if _db_client is None:
        return {"success": False, "error": "Database client not initialized"}
    result = await _db_client.preview_table(connection_id, database_name, schema_name, table_name, max_rows)
    return {"success": result.success, "data": result.data, "error": result.error}
