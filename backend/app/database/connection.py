"""
Database configuration and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from contextlib import asynccontextmanager
import os

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://purview:purview_password@localhost:5432/purview_db"
)

# Async database URL (for async operations)
ASYNC_DATABASE_URL = os.getenv(
    "ASYNC_DATABASE_URL",
    DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://") if DATABASE_URL.startswith("postgresql") else "sqlite+aiosqlite:///./purview.db"
)

# For SQLite fallback (development)
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Async engine for SQLite
    async_engine = create_async_engine(
        ASYNC_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL
    engine = create_engine(DATABASE_URL)
    async_engine = create_async_engine(ASYNC_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@asynccontextmanager
async def get_db_session():
    """Async context manager to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_async_db():
    """Async dependency to get database session."""
    async with get_db_session() as session:
        yield session

def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)

async def create_async_tables():
    """Create all database tables (async version)."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def drop_tables():
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)

async def drop_async_tables():
    """Drop all database tables (async version)."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
