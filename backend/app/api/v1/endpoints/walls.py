"""
Wall management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ....db.session import get_db
from ....models.schema import WallCreate, WallResponse
from ....services import storage
from ....core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("", response_model=WallResponse, status_code=status.HTTP_201_CREATED)
async def create_wall(
    wall_data: WallCreate,
    db: Session = Depends(get_db)
) -> WallResponse:
    """
    Create a new wall with optional obstacles.
    
    Args:
        wall_data: Wall creation data including dimensions and obstacles
        
    Returns:
        Created wall with ID
        
    Raises:
        HTTPException: If validation fails
    """
    try:
        # Extract obstacles as tuples
        obstacles = [
            (obs.x, obs.y, obs.width, obs.height)
            for obs in wall_data.obstacles
        ]
        
        wall = storage.create_wall(
            db=db,
            width=wall_data.width,
            height=wall_data.height,
            obstacles=obstacles
        )
        
        return WallResponse.model_validate(wall)
        
    except ValueError as e:
        logger.error(f"Validation error creating wall: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating wall: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create wall"
        )


@router.get("/{wall_id}", response_model=WallResponse)
async def get_wall(
    wall_id: int,
    db: Session = Depends(get_db)
) -> WallResponse:
    """
    Get wall by ID with obstacles.
    
    Args:
        wall_id: Wall identifier
        
    Returns:
        Wall data
        
    Raises:
        HTTPException: If wall not found
    """
    wall = storage.get_wall(db=db, wall_id=wall_id)
    
    if not wall:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wall {wall_id} not found"
        )
    
    return WallResponse.model_validate(wall)
