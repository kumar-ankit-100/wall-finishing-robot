"""
FastAPI main application.
"""
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import get_settings
from .core.logging import setup_logging, get_logger, set_request_id, get_request_id
from .core.metrics import get_metrics
from .db.session import create_database
from .api.v1 import api_router

settings = get_settings()
setup_logging()
logger = get_logger(__name__)
metrics = get_metrics()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    create_database()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down application")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging and metrics middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log requests and track metrics."""
    # Set request ID
    request_id = request.headers.get("X-Request-ID")
    set_request_id(request_id)
    
    # Track timing
    start_time = time.time()
    
    # Process request
    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000
        
        # Record metrics
        endpoint = f"{request.method} {request.url.path}"
        metrics.record_request(endpoint, duration_ms, response.status_code)
        
        # Log request
        logger.info(
            f"{request.method} {request.url.path}",
            extra={
                "method": request.method,
                "endpoint": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            }
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = get_request_id()
        
        return response
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            f"Request failed: {str(e)}",
            exc_info=True,
            extra={
                "method": request.method,
                "endpoint": request.url.path,
                "duration_ms": round(duration_ms, 2),
            }
        )
        
        # Record error
        endpoint = f"{request.method} {request.url.path}"
        metrics.record_request(endpoint, duration_ms, 500)
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
            headers={"X-Request-ID": get_request_id()}
        )


# Include API router
app.include_router(api_router, prefix=settings.api_v1_prefix)


# Metrics endpoint
@app.get("/metrics")
async def get_metrics_endpoint():
    """Get application metrics."""
    if not settings.enable_metrics:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Metrics disabled"}
        )
    
    return metrics.to_dict()


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": f"{settings.api_v1_prefix}/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
