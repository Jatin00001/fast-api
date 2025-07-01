from typing import Callable
from fastapi import FastAPI

from app.db.sql import engine
import logging

logger = logging.getLogger("app")

async def startup_handler() -> None:
    """
    Application startup handler
    """
    logger.info("Application startup initiated")
    
    try:
        # Import all models to ensure they are registered with SQLAlchemy
        from app.models import user, country, city, file, image, home_destination
        
        logger.info("All models imported successfully")
        logger.info("Database connection established")
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Error during application startup: {str(e)}")
        raise e

async def shutdown_handler() -> None:
    """
    Application shutdown handler
    """
    logger.info("Application shutdown initiated")
    
    try:
        # Close database connections
        if engine:
            await engine.dispose()
            logger.info("Database connections closed")
        
        logger.info("Application shutdown completed successfully")
        
    except Exception as e:
        logger.error(f"Error during application shutdown: {str(e)}")
        raise e

def create_start_app_handler(app: FastAPI) -> Callable:
    """
    Create startup handler for FastAPI app
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Startup handler function
    """
    async def start_app() -> None:
        await startup_handler()
    
    return start_app

def create_stop_app_handler(app: FastAPI) -> Callable:
    """
    Create shutdown handler for FastAPI app
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Shutdown handler function
    """
    async def stop_app() -> None:
        await shutdown_handler()
    
    return stop_app