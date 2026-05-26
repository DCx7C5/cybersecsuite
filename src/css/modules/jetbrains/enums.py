from enum import StrEnum, auto


class IDEToolCategory(StrEnum):
    FILE = auto()
    SEARCH = auto()
    CODE_ANALYSIS = auto()
    RUN = auto()
    REFACTOR = auto()
    DATABASE = auto()
    PROJECT = auto()


class SearchMode(StrEnum):
    TEXT = auto()
    REGEX = auto()
    SYMBOL = auto()
    GLOB = auto()
    FILENAME = auto()


class OperationStatus(StrEnum):
    SUCCESS = auto()
    ERROR = auto()
    TIMEOUT = auto()
    NOT_AVAILABLE = auto()


class IDEConnectionState(StrEnum):
    CONNECTED = auto()
    DISCONNECTED = auto()
    ERROR = auto()


class RefactorKind(StrEnum):
    RENAME = auto()
    EXTRACT_METHOD = auto()
    EXTRACT_VARIABLE = auto()
    MOVE_FILE = auto()
    SAFE_DELETE = auto()
