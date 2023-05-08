import datetime
import os

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app import get_db_session, AppContext
from app.internal.date_utils import is_weekends, current_time, current_period, \
    is_holiday
from app.main import app


def test_is_weekends():
    test_dates: dict[datetime.date, bool] = {
        datetime.date(2023, 5, 1): False,
        datetime.date(2023, 5, 5): True,
        datetime.date(2023, 5, 6): True,
        datetime.date(2023, 5, 7): True,
        datetime.date(2023, 5, 8): False,
    }
    for date, expected in test_dates.items():
        assert is_weekends(date) == expected


def test_current_time():
    now = datetime.datetime.now()
    result = current_time()
    assert (now.hour, now.minute) == (result.hour, result.minute)


@pytest.mark.asyncio
async def test_current_period():
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
    db_session = AsyncSession(bind=engine)
    assert await current_period(
        db_session=db_session,
        value=datetime.datetime(2022, 5, 1),
    ) == 'semester'
    await db_session.close()
    await engine.dispose()


@pytest.mark.asyncio
async def test_current_holiday_no_value():
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
    db_session = AsyncSession(bind=engine)
    assert (await is_holiday(
        db_session=db_session,
        value=datetime.date(2022, 5, 1),
    )) == 'normal'
    await db_session.close()
    await engine.dispose()


@pytest.mark.asyncio
async def test_current_holiday():
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
    db_session = AsyncSession(bind=engine)
    assert (await is_holiday(
        db_session=db_session,
        value=datetime.date(2023, 12, 25),
    )) == 'halt'
    await db_session.close()
    await engine.dispose()
