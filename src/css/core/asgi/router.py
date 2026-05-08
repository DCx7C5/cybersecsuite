
from css.core.logger import getLogger
from fastapi import APIRouter

logger = getLogger(__name__)


api_router = APIRouter(
    prefix="/api",
    tags=[
        "api",
    ]
)


a2a_router = APIRouter(
    prefix="/a2a",
    tags=[
        "a2a",
    ]
)