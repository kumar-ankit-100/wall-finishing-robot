"""
SQLAlchemy ORM models for the database.
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    ForeignKey,
    Index,
    JSON,
    Text,
)
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class Wall(Base):
    """Represents a wall to be finished."""
    
    __tablename__ = "walls"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    width: Mapped[float] = mapped_column(Float, nullable=False)  # meters
    height: Mapped[float] = mapped_column(Float, nullable=False)  # meters
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    
    # Relationships
    obstacles: Mapped[List["Obstacle"]] = relationship(
        "Obstacle", back_populates="wall", cascade="all, delete-orphan"
    )
    trajectories: Mapped[List["Trajectory"]] = relationship(
        "Trajectory", back_populates="wall", cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index("idx_walls_dims", "width", "height"),
    )
    
    def __repr__(self) -> str:
        return f"<Wall(id={self.id}, {self.width}m x {self.height}m)>"


class Obstacle(Base):
    """Represents a rectangular obstacle on a wall."""
    
    __tablename__ = "obstacles"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    wall_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("walls.id", ondelete="CASCADE"), nullable=False
    )
    x: Mapped[float] = mapped_column(Float, nullable=False)  # meters from origin
    y: Mapped[float] = mapped_column(Float, nullable=False)  # meters from origin
    width: Mapped[float] = mapped_column(Float, nullable=False)  # meters
    height: Mapped[float] = mapped_column(Float, nullable=False)  # meters
    
    # Relationships
    wall: Mapped["Wall"] = relationship("Wall", back_populates="obstacles")
    
    __table_args__ = (
        Index("idx_obstacles_wall", "wall_id"),
    )
    
    def __repr__(self) -> str:
        return f"<Obstacle(id={self.id}, pos=({self.x}, {self.y}), size={self.width}x{self.height})>"


class Trajectory(Base):
    """Represents a planned trajectory for a wall."""
    
    __tablename__ = "trajectories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    wall_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("walls.id", ondelete="CASCADE"), nullable=False
    )
    
    # Planner settings (stored as JSON)
    planner_settings: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Trajectory data (array of {x, y} points stored as JSON)
    points: Mapped[list] = mapped_column(JSON, nullable=False)
    
    # Computed metrics
    length_m: Mapped[float] = mapped_column(Float, nullable=False)  # total path length in meters
    duration_s: Mapped[float] = mapped_column(Float, nullable=False)  # estimated duration in seconds
    point_count: Mapped[int] = mapped_column(Integer, nullable=False)  # number of waypoints
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    
    # Relationships
    wall: Mapped["Wall"] = relationship("Wall", back_populates="trajectories")
    
    __table_args__ = (
        Index("idx_trajectories_wall", "wall_id"),
        Index("idx_trajectories_created", "created_at"),
        Index("idx_trajectories_pattern", "planner_settings"),  # JSON field index
    )
    
    def __repr__(self) -> str:
        pattern = self.planner_settings.get("pattern", "unknown")
        return f"<Trajectory(id={self.id}, wall_id={self.wall_id}, pattern={pattern}, points={self.point_count})>"
