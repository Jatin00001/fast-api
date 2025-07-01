from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
# from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.routes import router as api_router
from app.core.config import settings
from app.core.events import create_start_app_handler, create_stop_app_handler
from app.core.logging_config import setup_logging
import logging

# Initialize logging
setup_logging()
logger = logging.getLogger("app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting FastAPI application")
    startup_handler = create_start_app_handler(app)
    await startup_handler()
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application")
    shutdown_handler = create_stop_app_handler(app)
    await shutdown_handler()

# Initialize FastAPI with lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI project with PostgreSQL, AWS, and GCP support",
    version=settings.VERSION,
    docs_url="/docs",  # Always enable docs for development
    redoc_url="/redoc",  # Always enable redoc for development
    openapi_url="/openapi.json",  # Always enable openapi for development
    lifespan=lifespan,
)

# Configure TrustedHostMiddleware only for production
if not settings.DEBUG_MODE:
    try:
        from fastapi.middleware.trustedhost import TrustedHostMiddleware
        # In production, extract hosts from allowed origins
        import re
        allowed_hosts = []
        for origin in settings.allowed_origins_list:
            host = re.sub(r'^https?://', '', origin)
            host = host.split(':')[0]  # Remove port if present
            allowed_hosts.append(host)
        
        # Add testserver for testing purposes
        allowed_hosts.extend(["testserver", "localhost", "127.0.0.1"])
        
        # Only add TrustedHostMiddleware in production
        if allowed_hosts:
            app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
    except ImportError:
        pass  # TrustedHostMiddleware not available

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compression Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routes
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    """
    Root endpoint providing API information
    """
    logger.info("Root endpoint accessed")
    return {
        "status": 200,
        "message": "FastAPI API is running",
        "data": {
            "project": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "docs_url": "/docs" if settings.DEBUG_MODE else "/docs",
            "redoc_url": "/redoc" if settings.DEBUG_MODE else "/redoc"
        }
    }


if __name__ == "__main__":
    uvicorn_config = {
        "app": "main:app",
        "host": settings.HOST,
        "port": settings.PORT,
        "reload": settings.DEBUG_MODE,
        "workers": 1 if settings.DEBUG_MODE else 4,
        "proxy_headers": True,
        "forwarded_allow_ips": "*",
        "log_level": "info",
    }
    
    if settings.SSL_KEYFILE and settings.SSL_CERTFILE:
        uvicorn_config.update({
            "ssl_keyfile": settings.SSL_KEYFILE,
            "ssl_certfile": settings.SSL_CERTFILE,
        })
    
    logger.info("Starting application with uvicorn")
    uvicorn.run(**uvicorn_config)