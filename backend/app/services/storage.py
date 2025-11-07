"""
Storage service for trajectory CRUD operations.
"""
import time
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc

from ..db.models import Wall, Obstacle, Trajectory
from ..core.logging import get_logger
from ..core.metrics import get_metrics

logger = get_logger(__name__)
metrics = get_metrics()


def create_wall(
    db: Session,
    width: float,
    height: float,
    obstacles: List[Tuple[float, float, float, float]]
) -> Wall:
    """
    Create a wall with obstacles.
    
    Args:
        db: Database session
        width: Wall width in meters
        height: Wall height in meters
        obstacles: List of (x, y, width, height) tuples
        
    Returns:
        Created Wall instance
    """
    start_time = time.time()
    
    wall = Wall(width=width, height=height)
    db.add(wall)
    db.flush()  # Get wall ID for obstacles
    
    for x, y, w, h in obstacles:
        obs = Obstacle(
            wall_id=wall.id,
            x=x, y=y,
            width=w, height=h
        )
        db.add(obs)
    
    db.commit()
    db.refresh(wall)
    
    duration_ms = (time.time() - start_time) * 1000
    metrics.record_db_query(duration_ms)
    metrics.record_wall_created()
    
    logger.info(
        f"Created wall {wall.id} ({width}x{height}m) with {len(obstacles)} obstacles",
        extra={"duration_ms": duration_ms}
    )
    
    return wall


def get_wall(db: Session, wall_id: int) -> Optional[Wall]:
    """
    Get wall by ID with obstacles.
    
    Args:
        db: Database session
        wall_id: Wall ID
        
    Returns:
        Wall instance or None
    """
    start_time = time.time()
    
    wall = db.query(Wall).options(
        joinedload(Wall.obstacles)
    ).filter(Wall.id == wall_id).first()
    
    duration_ms = (time.time() - start_time) * 1000
    metrics.record_db_query(duration_ms)
    
    return wall


def create_trajectory(
    db: Session,
    wall_id: int,
    planner_settings: dict,
    points: List[dict],
    length_m: float,
    duration_s: float,
) -> Trajectory:
    """
    Create a trajectory.
    
    Args:
        db: Database session
        wall_id: Associated wall ID
        planner_settings: Planner configuration as dict
        points: List of {x, y} waypoints
        length_m: Total path length
        duration_s: Estimated duration
        
    Returns:
        Created Trajectory instance
    """
    start_time = time.time()
    
    trajectory = Trajectory(
        wall_id=wall_id,
        planner_settings=planner_settings,
        points=points,
        length_m=length_m,
        duration_s=duration_s,
        point_count=len(points),
    )
    
    db.add(trajectory)
    db.commit()
    db.refresh(trajectory)
    
    duration_ms = (time.time() - start_time) * 1000
    metrics.record_db_query(duration_ms)
    metrics.record_trajectory_created()
    
    logger.info(
        f"Created trajectory {trajectory.id} for wall {wall_id} "
        f"with {len(points)} points",
        extra={"duration_ms": duration_ms}
    )
    
    return trajectory


def get_trajectory(db: Session, trajectory_id: int, include_wall: bool = False) -> Optional[Trajectory]:
    """
    Get trajectory by ID.
    
    Args:
        db: Database session
        trajectory_id: Trajectory ID
        include_wall: Whether to load wall data
        
    Returns:
        Trajectory instance or None
    """
    start_time = time.time()
    
    query = db.query(Trajectory)
    if include_wall:
        query = query.options(
            joinedload(Trajectory.wall).joinedload(Wall.obstacles)
        )
    
    trajectory = query.filter(Trajectory.id == trajectory_id).first()
    
    duration_ms = (time.time() - start_time) * 1000
    metrics.record_db_query(duration_ms)
    
    return trajectory


def list_trajectories(
    db: Session,
    wall_id: Optional[int] = None,
    pattern: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> Tuple[List[Trajectory], int]:
    """
    List trajectories with optional filters.
    
    Args:
        db: Database session
        wall_id: Filter by wall ID
        pattern: Filter by pattern name
        limit: Maximum results
        offset: Result offset
        
    Returns:
        Tuple of (trajectories list, total count)
    """
    start_time = time.time()
    
    query = db.query(Trajectory)
    
    if wall_id is not None:
        query = query.filter(Trajectory.wall_id == wall_id)
    
    # Note: Filtering on JSON field - SQLite has limited JSON support
    # For production, consider extracting pattern to a separate column
    
    total = query.count()
    
    trajectories = query.order_by(
        desc(Trajectory.created_at)
    ).limit(limit).offset(offset).all()
    
    duration_ms = (time.time() - start_time) * 1000
    metrics.record_db_query(duration_ms)
    
    return trajectories, total


def delete_trajectory(db: Session, trajectory_id: int) -> bool:
    """
    Delete trajectory by ID.
    
    Args:
        db: Database session
        trajectory_id: Trajectory ID
        
    Returns:
        True if deleted, False if not found
    """
    start_time = time.time()
    
    trajectory = db.query(Trajectory).filter(
        Trajectory.id == trajectory_id
    ).first()
    
    if not trajectory:
        return False
    
    db.delete(trajectory)
    db.commit()
    
    duration_ms = (time.time() - start_time) * 1000
    metrics.record_db_query(duration_ms)
    
    logger.info(
        f"Deleted trajectory {trajectory_id}",
        extra={"duration_ms": duration_ms}
    )
    
    return True
