#!/usr/bin/env python3
"""
Seed database with sample data for testing.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.db.session import SessionLocal, create_database
from backend.app.services import storage, planner
from backend.app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def main():
    """Seed database with sample walls and trajectories."""
    logger.info("Seeding database with sample data...")
    
    # Ensure database exists
    create_database()
    
    db = SessionLocal()
    
    try:
        # Sample 1: Assignment example - 5m x 5m wall with 0.25m x 0.25m window
        logger.info("Creating sample 1: 5m x 5m with window obstacle")
        wall1 = storage.create_wall(
            db=db,
            width=5.0,
            height=5.0,
            obstacles=[(2.0, 2.0, 0.25, 0.25)]
        )
        
        # Generate zigzag trajectory
        plan1 = planner.create_plan(
            wall_width=wall1.width,
            wall_height=wall1.height,
            obstacles=[(obs.x, obs.y, obs.width, obs.height) for obs in wall1.obstacles],
            pattern="zigzag",
            spacing=0.05,
            speed=0.1
        )
        
        traj1 = storage.create_trajectory(
            db=db,
            wall_id=wall1.id,
            planner_settings={"pattern": "zigzag", "spacing": 0.05, "speed": 0.1},
            points=plan1["points"],
            length_m=plan1["length_m"],
            duration_s=plan1["duration_s"]
        )
        logger.info(f"Created trajectory {traj1.id} with {traj1.point_count} points")
        
        # Sample 2: Small wall with no obstacles
        logger.info("Creating sample 2: 2m x 2m with no obstacles")
        wall2 = storage.create_wall(
            db=db,
            width=2.0,
            height=2.0,
            obstacles=[]
        )
        
        # Generate spiral trajectory
        plan2 = planner.create_plan(
            wall_width=wall2.width,
            wall_height=wall2.height,
            obstacles=[],
            pattern="spiral",
            spacing=0.1,
            speed=0.15
        )
        
        traj2 = storage.create_trajectory(
            db=db,
            wall_id=wall2.id,
            planner_settings={"pattern": "spiral", "spacing": 0.1, "speed": 0.15},
            points=plan2["points"],
            length_m=plan2["length_m"],
            duration_s=plan2["duration_s"]
        )
        logger.info(f"Created trajectory {traj2.id} with {traj2.point_count} points")
        
        # Sample 3: Large wall with multiple obstacles
        logger.info("Creating sample 3: 10m x 8m with multiple obstacles")
        wall3 = storage.create_wall(
            db=db,
            width=10.0,
            height=8.0,
            obstacles=[
                (2.0, 2.0, 1.0, 1.5),  # Window 1
                (6.0, 3.0, 0.5, 1.0),  # Window 2
                (4.0, 6.0, 1.5, 0.8),  # Vent
            ]
        )
        
        plan3 = planner.create_plan(
            wall_width=wall3.width,
            wall_height=wall3.height,
            obstacles=[(obs.x, obs.y, obs.width, obs.height) for obs in wall3.obstacles],
            pattern="zigzag",
            spacing=0.08,
            speed=0.12
        )
        
        traj3 = storage.create_trajectory(
            db=db,
            wall_id=wall3.id,
            planner_settings={"pattern": "zigzag", "spacing": 0.08, "speed": 0.12},
            points=plan3["points"],
            length_m=plan3["length_m"],
            duration_s=plan3["duration_s"]
        )
        logger.info(f"Created trajectory {traj3.id} with {traj3.point_count} points")
        
        logger.info("✅ Database seeded successfully!")
        logger.info(f"Created {3} walls and {3} trajectories")
        
    except Exception as e:
        logger.error(f"Error seeding database: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
