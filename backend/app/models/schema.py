"""
Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Obstacle Schemas
# ============================================================================

class ObstacleBase(BaseModel):
    """Base obstacle schema."""
    x: float = Field(..., ge=0, description="X coordinate in meters")
    y: float = Field(..., ge=0, description="Y coordinate in meters")
    width: float = Field(..., gt=0, description="Width in meters")
    height: float = Field(..., gt=0, description="Height in meters")


class ObstacleCreate(ObstacleBase):
    """Schema for creating an obstacle."""
    pass


class ObstacleResponse(ObstacleBase):
    """Schema for obstacle response."""
    id: int
    wall_id: int
    
    class Config:
        from_attributes = True


# ============================================================================
# Wall Schemas
# ============================================================================

class WallBase(BaseModel):
    """Base wall schema."""
    width: float = Field(..., gt=0, description="Wall width in meters")
    height: float = Field(..., gt=0, description="Wall height in meters")


class WallCreate(WallBase):
    """Schema for creating a wall with obstacles."""
    obstacles: List[ObstacleCreate] = Field(default_factory=list)
    
    @field_validator("obstacles")
    @classmethod
    def validate_obstacles(cls, v, info):
        """Validate obstacles are within wall bounds."""
        if "width" in info.data and "height" in info.data:
            wall_width = info.data["width"]
            wall_height = info.data["height"]
            
            for obs in v:
                if obs.x + obs.width > wall_width:
                    raise ValueError(
                        f"Obstacle extends beyond wall width: "
                        f"x={obs.x}, width={obs.width}, wall_width={wall_width}"
                    )
                if obs.y + obs.height > wall_height:
                    raise ValueError(
                        f"Obstacle extends beyond wall height: "
                        f"y={obs.y}, height={obs.height}, wall_height={wall_height}"
                    )
        return v


class WallResponse(WallBase):
    """Schema for wall response."""
    id: int
    created_at: datetime
    obstacles: List[ObstacleResponse] = []
    
    class Config:
        from_attributes = True


# ============================================================================
# Trajectory Schemas
# ============================================================================

class Point(BaseModel):
    """A 2D point in the trajectory."""
    x: float = Field(..., description="X coordinate in meters")
    y: float = Field(..., description="Y coordinate in meters")


class PlannerSettings(BaseModel):
    """Settings for the coverage planner."""
    pattern: Literal["zigzag", "spiral"] = Field(
        default="zigzag",
        description="Coverage pattern to use"
    )
    spacing: float = Field(
        default=0.05,
        gt=0,
        le=1.0,
        description="Spacing between passes in meters"
    )
    speed: float = Field(
        default=0.1,
        gt=0,
        le=2.0,
        description="Robot speed in meters per second"
    )
    clearance: float = Field(
        default=0.02,
        ge=0,
        le=0.5,
        description="Clearance from obstacles in meters"
    )
    resolution: float = Field(
        default=0.01,
        gt=0,
        le=0.1,
        description="Path resolution in meters"
    )


class PlanRequest(BaseModel):
    """Request to generate a trajectory plan."""
    settings: PlannerSettings = Field(default_factory=PlannerSettings)


class TrajectoryBase(BaseModel):
    """Base trajectory schema."""
    wall_id: int
    planner_settings: dict
    length_m: float = Field(..., ge=0)
    duration_s: float = Field(..., ge=0)
    point_count: int = Field(..., ge=0)


class TrajectoryResponse(TrajectoryBase):
    """Schema for trajectory response without full points."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class TrajectoryDetailResponse(TrajectoryResponse):
    """Schema for detailed trajectory response with all points."""
    points: List[Point]
    wall: Optional[WallResponse] = None


class TrajectoryListResponse(BaseModel):
    """Paginated list of trajectories."""
    items: List[TrajectoryResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


# ============================================================================
# Health & Metrics Schemas
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime
    database: str


class MetricsResponse(BaseModel):
    """Metrics response."""
    requests: dict
    planner: dict
    database: dict
    entities: dict
    endpoints: dict
