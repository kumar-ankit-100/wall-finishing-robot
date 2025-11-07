"""
Structured logging configuration with request tracking.
"""
import logging
import sys
import json
import time
from typing import Any
from contextvars import ContextVar
from uuid import uuid4

from .config import get_settings

# Context variable for request ID
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add request ID if available
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id
        
        # Add extra fields
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        if hasattr(record, "endpoint"):
            log_data["endpoint"] = record.endpoint
        if hasattr(record, "method"):
            log_data["method"] = record.method
            
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Human-readable text formatter."""
    
    def format(self, record: logging.LogRecord) -> str:
        request_id = request_id_var.get()
        prefix = f"[{request_id[:8]}] " if request_id else ""
        
        message = super().format(record)
        return f"{prefix}{message}"


def setup_logging() -> None:
    """Configure application logging."""
    settings = get_settings()
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Set formatter based on config
    if settings.log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


def set_request_id(request_id: str | None = None) -> str:
    """Set request ID for current context."""
    if request_id is None:
        request_id = str(uuid4())
    request_id_var.set(request_id)
    return request_id


def get_request_id() -> str:
    """Get current request ID."""
    return request_id_var.get()
