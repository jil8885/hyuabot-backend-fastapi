# -*- coding: utf-8 -*-
"""Module that contains database dependancies to use in the app.

Attributes:
    database_host (str): Address of the database.
    database_port (int): Port of the database.
    database_name (str): Name of the database.
    database_user (str): User of the database.
    database_password (str): Password of the database.
    engine (sqlalchemy.ext.asyncio.AsyncEngine): Database engine.
"""
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Get database engine.
database_host = os.getenv('DB_HOST')
database_port = os.getenv('DB_PORT')
database_name = os.getenv('DB_NAME')
database_user = os.getenv('DB_USER')
database_password = os.getenv('DB_PASSWORD')
engine = create_async_engine(
    f'postgresql+asyncpg://{database_user}:{database_password}@'
    f'{database_host}:{database_port}/{database_name}',
    echo=True,
    pool_pre_ping=True,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Function to get database session from any place in the application.
        Yields:
            AsyncSession: Database session.
    """
    session = AsyncSession(bind=engine)
    try:
        yield session
    finally:
        await session.close()
