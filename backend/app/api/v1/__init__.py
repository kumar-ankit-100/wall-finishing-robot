"""
API v1 router configuration.
"""
from fastapi import APIRouter
from .endpoints import health, walls, trajectories

api_router = APIRouter()

api_router.include_router(
    health.router,
    tags=["health"]
)

api_router.include_router(
    walls.router,
    prefix="/walls",
    tags=["walls"]
)

api_router.include_router(
    trajectories.router,
    prefix="/trajectories",
    tags=["trajectories"]
)
