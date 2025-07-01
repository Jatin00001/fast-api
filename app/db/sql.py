# from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import QueuePool
from sqlalchemy import event, text
from app.core.config import settings

# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from typing import AsyncGenerator
import logging

logger = logging.getLogger("database")

# Create async engine with optimized pool settings
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG_MODE,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={} if settings.DATABASE_URL.startswith('postgresql') else {"check_same_thread": False}
)

# Create sessionmaker with optimized settings
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Create base class for declarative models
Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session with proper error handling and connection management
    """
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        await session.rollback()
        raise e
    finally:
        await session.close()

# Add event listeners for connection pool management
@event.listens_for(engine.sync_engine, "connect")
def connect(dbapi_connection, connection_record):
    connection_record.info['pid'] = id(dbapi_connection)

@event.listens_for(engine.sync_engine, "checkout")
def checkout(dbapi_connection, connection_record, connection_proxy):
    pid = id(dbapi_connection)
    if connection_record.info['pid'] != pid:
        connection_record.connection = connection_proxy.connection = None
        raise DisconnectionError(
            "Connection record belongs to pid %s, "
            "attempting to check out in pid %s" %
            (connection_record.info['pid'], pid)
        )

class DisconnectionError(Exception):
    pass

