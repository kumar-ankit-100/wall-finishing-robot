"""
Trajectory management endpoints.
"""
import time
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ....db.session import get_db
from ....models.schema import (
    PlanRequest,
    TrajectoryResponse,
    TrajectoryDetailResponse,
    TrajectoryListResponse,
    Point,
)
from ....services import storage, planner
from ....core.logging import get_logger
from ....core.metrics import get_metrics
from ....core.config import get_settings

router = APIRouter()
logger = get_logger(__name__)
metrics = get_metrics()
settings = get_settings()


@router.post(
    "/walls/{wall_id}/plan",
    response_model=TrajectoryResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_plan(
    wall_id: int,
    plan_request: PlanRequest,
    db: Session = Depends(get_db)
) -> TrajectoryResponse:
    """
    Generate and store a coverage plan for a wall.
    
    Args:
        wall_id: Wall identifier
        plan_request: Planning parameters
        
    Returns:
        Created trajectory metadata
        
    Raises:
        HTTPException: If wall not found or planning fails
    """
    # Get wall with obstacles
    wall = storage.get_wall(db=db, wall_id=wall_id)
    if not wall:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wall {wall_id} not found"
        )
    
    # Extract obstacles
    obstacles = [
        (obs.x, obs.y, obs.width, obs.height)
        for obs in wall.obstacles
    ]
    
    # Run planner
    start_time = time.time()
    try:
        plan_result = planner.create_plan(
            wall_width=wall.width,
            wall_height=wall.height,
            obstacles=obstacles,
            pattern=plan_request.settings.pattern,
            spacing=plan_request.settings.spacing,
            clearance=plan_request.settings.clearance,
            resolution=plan_request.settings.resolution,
            speed=plan_request.settings.speed,
        )
    except ValueError as e:
        logger.error(f"Planning failed for wall {wall_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Planning failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during planning: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Planning failed due to internal error"
        )
    
    planner_duration_ms = (time.time() - start_time) * 1000
    metrics.record_planner_run(planner_duration_ms)
    
    # Check point count limit
    if plan_result["point_count"] > settings.max_trajectory_points:
        logger.warning(
            f"Trajectory has {plan_result['point_count']} points, "
            f"exceeds limit of {settings.max_trajectory_points}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trajectory too large ({plan_result['point_count']} points). "
                   f"Try increasing spacing or resolution."
        )
    
    # Store trajectory
    try:
        trajectory = storage.create_trajectory(
            db=db,
            wall_id=wall_id,
            planner_settings=plan_request.settings.model_dump(),
            points=plan_result["points"],
            length_m=plan_result["length_m"],
            duration_s=plan_result["duration_s"],
        )
    except Exception as e:
        logger.error(f"Failed to store trajectory: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store trajectory"
        )
    
    logger.info(
        f"Created trajectory {trajectory.id} for wall {wall_id}",
        extra={
            "planner_duration_ms": planner_duration_ms,
            "point_count": trajectory.point_count,
            "length_m": trajectory.length_m,
        }
    )
    
    return TrajectoryResponse.model_validate(trajectory)


@router.get("/{trajectory_id}", response_model=TrajectoryDetailResponse)
async def get_trajectory(
    trajectory_id: int,
    include_wall: bool = Query(False, description="Include wall data in response"),
    db: Session = Depends(get_db)
) -> TrajectoryDetailResponse:
    """
    Get trajectory by ID with all waypoints.
    
    Args:
        trajectory_id: Trajectory identifier
        include_wall: Whether to include wall data
        
    Returns:
        Complete trajectory data
        
    Raises:
        HTTPException: If trajectory not found
    """
    trajectory = storage.get_trajectory(
        db=db,
        trajectory_id=trajectory_id,
        include_wall=include_wall
    )
    
    if not trajectory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trajectory {trajectory_id} not found"
        )
    
    # Convert points
    response_data = TrajectoryDetailResponse.model_validate(trajectory)
    
    return response_data


@router.get("", response_model=TrajectoryListResponse)
async def list_trajectories(
    wall_id: Optional[int] = Query(None, description="Filter by wall ID"),
    pattern: Optional[str] = Query(None, description="Filter by pattern"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
) -> TrajectoryListResponse:
    """
    List trajectories with pagination and optional filters.
    
    Args:
        wall_id: Optional wall ID filter
        pattern: Optional pattern filter
        page: Page number (1-indexed)
        page_size: Items per page
        
    Returns:
        Paginated list of trajectories
    """
    offset = (page - 1) * page_size
    
    trajectories, total = storage.list_trajectories(
        db=db,
        wall_id=wall_id,
        pattern=pattern,
        limit=page_size,
        offset=offset
    )
    
    items = [TrajectoryResponse.model_validate(t) for t in trajectories]
    
    return TrajectoryListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(offset + len(items)) < total
    )


@router.delete("/{trajectory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trajectory(
    trajectory_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete trajectory by ID.
    
    Args:
        trajectory_id: Trajectory identifier
        
    Raises:
        HTTPException: If trajectory not found
    """
    deleted = storage.delete_trajectory(db=db, trajectory_id=trajectory_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trajectory {trajectory_id} not found"
        )
    
    logger.info(f"Deleted trajectory {trajectory_id}")
