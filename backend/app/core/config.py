"""
Application configuration management.
"""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = "Wall Finishing Robot API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database
    database_url: str = "sqlite:///./wall_robot.db"
    database_echo: bool = False
    
    # API
    api_v1_prefix: str = "/v1"
    # cors_origins: list[str] = ["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"]
    
    # Planning
    default_spacing_m: float = 0.2  # 20cm default spacing (reasonable for demo)
    default_robot_speed_ms: float = 0.1  # 10cm/s default speed
    max_trajectory_points: int = 50000  # Allow up to 50k points
    
    # Performance
    max_payload_size_mb: int = 10
    rate_limit_requests: int = 100
    rate_limit_window_s: int = 60
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # json or text
    
    # Metrics
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
