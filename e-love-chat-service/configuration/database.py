# database.py

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import colorlog
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from configuration.config import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)s - %(message)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

DATABASE_URL = settings.database_url

if not DATABASE_URL:
    logger.error("DATABASE_URL is not set in environment variables.")
    raise ValueError("DATABASE_URL must be set in environment variables.")

try:
    engine = create_async_engine(DATABASE_URL)
    logger.info("Async SQLAlchemy engine created successfully.")
except Exception as e:
    logger.error(f"Failed to create async SQLAlchemy engine: {e}")
    raise

Base = declarative_base()
logger.info("Starting database connection check...")


AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except HTTPException as he:
            await session.rollback()
            raise he
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise e
