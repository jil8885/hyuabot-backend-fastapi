"""Main entry point for the application.
Attributes:
    app (FastAPI): FastAPI application.
    app_settings (AppSettings): Application settings.
    hypercorn_config (Config): Hypercorn configuration.
"""
from hypercorn.config import Config

from app import create_app, AppSettings

hypercorn_config = Config()
app_settings = AppSettings()
app = create_app(app_settings)
