import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)


api_router = APIRouter(
    prefix="/api",
    tags=[
        "api",
    ]
)


a2a_router = APIRouter(
    prefix="/google_a2a",
    tags=[
        "marketplace",
    ]
)