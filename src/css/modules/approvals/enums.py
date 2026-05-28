from enum import Enum


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

class ApprovalDecision(str, Enum):
    REQUIRED = "REQUIRED"
    ALLOWED = "ALLOWED"
    DENIED = "DENIED"

__all__ = [
    "ApprovalStatus",
    "ApprovalDecision",
]
