"""
API dependencies.
"""
from fastapi import Request
from ..core.logging import set_request_id, get_request_id


async def get_current_request_id(request: Request) -> str:
    """Get or create request ID for current request."""
    request_id = request.headers.get("X-Request-ID")
    return set_request_id(request_id)
