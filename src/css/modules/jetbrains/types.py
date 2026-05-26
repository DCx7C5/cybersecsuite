from typing import Any

import msgspec


class FileLocation(msgspec.Struct, frozen=True, kw_only=True):
    path: str
    line: int | None = None
    column: int | None = None


class RunConfiguration(msgspec.Struct, frozen=True, kw_only=True):
    name: str
    program_arguments: str | None = None
    working_directory: str | None = None
    envs: dict[str, str] | None = None


class SearchQuery(msgspec.Struct, frozen=True, kw_only=True):
    pattern: str
    mode: str = "text"
    case_sensitive: bool = True
    file_mask: str | None = None
    max_results: int = 50


class SearchMatch(msgspec.Struct, frozen=True, kw_only=True):
    file: str
    line: int
    column: int
    snippet: str
    match_text: str = ""


class IDEOperationResult(msgspec.Struct, frozen=True, kw_only=True):
    success: bool
    status: str = "SUCCESS"
    data: Any = None
    error: str | None = None
    duration_ms: float = 0.0


class CodeAnalysisProblem(msgspec.Struct, frozen=True, kw_only=True):
    file: str
    line: int
    column: int
    severity: str
    message: str
    rule: str | None = None


class DBConnection(msgspec.Struct, frozen=True, kw_only=True):
    id: str
    name: str
    type: str = ""


class DBSchema(msgspec.Struct, frozen=True, kw_only=True):
    name: str


class DBObject(msgspec.Struct, frozen=True, kw_only=True):
    name: str
    kind: str
    schema_name: str


class QueryResult(msgspec.Struct, frozen=True, kw_only=True):
    columns: list[str]
    rows: list[list[Any]]
    row_count: int = 0
    duration_ms: float = 0.0
    error: str | None = None


class TablePreview(msgspec.Struct, frozen=True, kw_only=True):
    table: str
    schema_name: str
    columns: list[dict[str, Any]]
    rows: list[list[Any]]
    total_rows: int = 0


class SymbolInfo(msgspec.Struct, frozen=True, kw_only=True):
    name: str
    kind: str
    file: str
    line: int
    column: int
    signature: str = ""
    documentation: str = ""


class ProjectInfo(msgspec.Struct, frozen=True, kw_only=True):
    modules: list[str]
    dependencies: list[str]
    repositories: list[str]
    open_files: list[str]
