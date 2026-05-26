from css.core.exceptions import BaseModuleException


class IDEError(BaseModuleException):
    ...


class IDEConnectionError(IDEError):
    ...


class IDEOperationError(IDEError):
    ...


class IDETimeoutError(IDEError):
    ...


class IDENotAvailableError(IDEError):
    ...
