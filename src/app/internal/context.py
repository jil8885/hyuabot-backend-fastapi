# This module contains the application context.
from __future__ import annotations

from typing import NamedTuple, TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncEngine


if TYPE_CHECKING:
    from app.internal.config import AppSettings
    from app.internal.app import App


class AppContext(NamedTuple):
    """Class that contains the application context.
    Attributes:
        app_settings (AppSettings): Application settings.
        db_engine (AsyncEngine): Database engine.
    """
    app_settings: AppSettings
    db_engine: AsyncEngine

    @staticmethod
    def from_app(app: App) -> AppContext:
        """Function to get application context from any place in the app.
        Args:
            app (App): FastAPI application.
        Returns:
            AppContext: Application context.
        Raises:
            RuntimeError: If the application context is not initialized.
        """
        try:
            return app.extra.context
        except AttributeError:
            raise RuntimeError('App context is not initialized')
