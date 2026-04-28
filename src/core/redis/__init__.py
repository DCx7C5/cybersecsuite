"""Redis-backed messaging infrastructure for inter-entity communication."""

from .communicator import RedisCommunicator
from .dispatcher import MessageDispatcher
from .messaging import Message

__all__ = [
    "Message",
    "MessageDispatcher",
    "RedisCommunicator",
]
