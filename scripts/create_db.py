#!/usr/bin/env python3
"""
Create and initialize the database.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.db.session import create_database
from backend.app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def main():
    """Create database tables."""
    logger.info("Creating database tables...")
    create_database()
    logger.info("Database created successfully!")


if __name__ == "__main__":
    main()
