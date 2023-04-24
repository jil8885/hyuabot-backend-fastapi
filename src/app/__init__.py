# Module for creating FastAPI app and adding middleware and routers.
import functools

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from app.controller.library import library_router
from app.dependancies.database import get_db_session
from app.internal.app import App
from app.internal.config import AppSettings
from app.internal.context import AppContext
from app.controller.campus import campus_router


async def get_context(db_session: AsyncSession = Depends(get_db_session)) \
        -> dict[str, AsyncSession]:
    """Function to get the application context.
    Args:
        db_session (AsyncSession): Database session.
    Returns:
        dict[str, AsyncSession]: Application context.
    """
    return {'db_session': db_session}


def create_app(settings: AppSettings) -> App:
    """Function to create the FastAPI application.
    Args:
        settings (AppSettings): Application settings.
    Returns:
        FastAPIWithContext: FastAPI application.
    """
    app = App()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_event_handler(
        'startup',
        functools.partial(_web_app_startup, app=app, settings=settings),
    )
    app.add_event_handler(
        'shutdown',
        functools.partial(_web_app_shutdown, app=app),
    )
    app.extra.settings = settings
    app.include_router(campus_router, prefix='/campus', tags=['campus'])
    app.include_router(library_router, prefix='/library', tags=['library'])
    return app


async def _web_app_startup(app: App, settings: AppSettings) -> None:
    """Function to execute on startup.
    Args:
        app (App): FastAPI application.
        settings (AppSettings): Application settings.
    """
    database_engine = create_async_engine(
        settings.DATABASE_URI,
        echo=True,
        pool_pre_ping=True,
    )
    context = AppContext(app_settings=settings, db_engine=database_engine)
    app.extra.context = context


async def _web_app_shutdown(app: App) -> None:
    """Function to execute on shutdown.
    Args:
        app (App): FastAPI application.
    """
    context = AppContext.from_app(app)
    await context.db_engine.dispose()
