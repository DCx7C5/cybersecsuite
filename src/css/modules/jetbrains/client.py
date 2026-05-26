
from .enums import OperationStatus
from .types import (
    FileLocation,
    IDEOperationResult,
    ProjectInfo,
    RunConfiguration,
    SearchQuery,
)


class PyCharmToolClient:
    def __init__(self) -> None:
        self._available = True

    @property
    def is_available(self) -> bool:
        return self._available

    # ── File operations ──────────────────────────────────────────────

    async def read_file(self, path: str) -> IDEOperationResult:
        return IDEOperationResult(success=True, data="", status=OperationStatus.SUCCESS)

    async def get_file_text(self, path: str) -> IDEOperationResult:
        return IDEOperationResult(success=True, data="", status=OperationStatus.SUCCESS)

    async def create_file(self, path: str, content: str = "") -> IDEOperationResult:
        return IDEOperationResult(success=True, status=OperationStatus.SUCCESS)

    async def replace_text(
        self,
        path: str,
        old_text: str,
        new_text: str,
        replace_all: bool = True,
        case_sensitive: bool = True,
        regex: bool = False,
    ) -> IDEOperationResult:
        return IDEOperationResult(success=True, data=0, status=OperationStatus.SUCCESS)

    async def reformat_file(self, path: str) -> IDEOperationResult:
        return IDEOperationResult(success=True, status=OperationStatus.SUCCESS)

    async def open_file(self, location: FileLocation) -> IDEOperationResult:
        return IDEOperationResult(success=True, status=OperationStatus.SUCCESS)

    # ── Search operations ────────────────────────────────────────────

    async def search_text(self, query: SearchQuery) -> IDEOperationResult:
        return IDEOperationResult(success=True, data=[], status=OperationStatus.SUCCESS)

    async def search_regex(self, query: SearchQuery) -> IDEOperationResult:
        return IDEOperationResult(success=True, data=[], status=OperationStatus.SUCCESS)

    async def search_symbol(self, name: str) -> IDEOperationResult:
        return IDEOperationResult(success=True, data=[], status=OperationStatus.SUCCESS)

    async def find_files_by_glob(self, pattern: str) -> IDEOperationResult:
        return IDEOperationResult(success=True, data=[], status=OperationStatus.SUCCESS)

    async def find_files_by_name(self, keyword: str) -> IDEOperationResult:
        return IDEOperationResult(success=True, data=[], status=OperationStatus.SUCCESS)

    # ── Code analysis ────────────────────────────────────────────────

    async def get_file_problems(self, path: str) -> IDEOperationResult:
        return IDEOperationResult(success=True, data=[], status=OperationStatus.SUCCESS)

    async def get_symbol_info(self, path: str, line: int, column: int) -> IDEOperationResult:
        return IDEOperationResult(success=True, status=OperationStatus.SUCCESS)

    async def build_project(self) -> IDEOperationResult:
        return IDEOperationResult(success=True, data=[], status=OperationStatus.SUCCESS)

    # ── Run operations ───────────────────────────────────────────────

    async def list_run_configurations(self) -> IDEOperationResult:
        return IDEOperationResult(success=True, data=[], status=OperationStatus.SUCCESS)

    async def execute_run_configuration(
        self,
        config: RunConfiguration,
        wait_for_exit: bool = True,
        timeout_ms: int = 120_000,
    ) -> IDEOperationResult:
        return IDEOperationResult(success=True, data={}, status=OperationStatus.SUCCESS)

    # ── Refactoring ──────────────────────────────────────────────────

    async def rename_symbol(self, path: str, old_name: str, new_name: str) -> IDEOperationResult:
        return IDEOperationResult(success=True, status=OperationStatus.SUCCESS)

    # ── Project info ─────────────────────────────────────────────────

    async def get_project_info(self) -> IDEOperationResult:
        return IDEOperationResult(
            success=True,
            data=ProjectInfo(modules=[], dependencies=[], repositories=[], open_files=[]),
            status=OperationStatus.SUCCESS,
        )

    async def list_directory_tree(self, path: str, max_depth: int = 3) -> IDEOperationResult:
        return IDEOperationResult(success=True, data=[], status=OperationStatus.SUCCESS)
