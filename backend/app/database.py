"""
Database configuration and connection setup.

This module handles database connection, session management, and configuration.
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./acbc.db")

# Create async engine
engine = create_async_engine(
    DATABASE_URL, 
    echo=True,
    pool_pre_ping=True,
    pool_recycle=300
)

AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """Get async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()