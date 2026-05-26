
from .enums import OperationStatus
from .types import (
    DBConnection,
    DBSchema,
    DBObject,
    IDEOperationResult,
    QueryResult,
    TablePreview,
)


class DatabaseClient:
    def __init__(self) -> None:
        self._available = True

    @property
    def is_available(self) -> bool:
        return self._available

    async def list_connections(self) -> IDEOperationResult[list[DBConnection]]:
        return IDEOperationResult(success=True, data=[], status=OperationStatus.SUCCESS)

    async def list_schemas(self, connection_id: str, selected_only: bool = True) -> IDEOperationResult[list[DBSchema]]:
        return IDEOperationResult(success=True, data=[], status=OperationStatus.SUCCESS)

    async def list_schema_objects(
        self,
        connection_id: str,
        database_name: str,
        schema_name: str,
        kind: str | None = None,
    ) -> IDEOperationResult[list[DBObject]]:
        return IDEOperationResult(success=True, data=[], status=OperationStatus.SUCCESS)

    async def get_object_description(
        self,
        connection_id: str,
        database_name: str,
        schema_name: str,
        kind: str,
        object_name: str,
    ) -> IDEOperationResult[str]:
        return IDEOperationResult(success=True, data="", status=OperationStatus.SUCCESS)

    async def execute_query(
        self,
        connection_id: str,
        database_name: str,
        schema_name: str,
        query: str,
    ) -> IDEOperationResult[QueryResult]:
        return IDEOperationResult(success=True, status=OperationStatus.SUCCESS)

    async def preview_table(
        self,
        connection_id: str,
        database_name: str,
        schema_name: str,
        table_name: str,
        max_rows: int = 100,
    ) -> IDEOperationResult[TablePreview]:
        return IDEOperationResult(success=True, status=OperationStatus.SUCCESS)

    async def test_connection(self, connection_id: str) -> IDEOperationResult[bool]:
        return IDEOperationResult(success=True, data=False, status=OperationStatus.SUCCESS)
