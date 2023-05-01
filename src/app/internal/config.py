# Module for application-wide settings.
import os

from pydantic import BaseSettings, Field


class AppSettings(BaseSettings):
    """Class that contains the application-wide settings.
    Attributes:
        DATABASE_URI(str): The URI of the database.
    """
    DATABASE_URI: str = Field(
        default=f"postgresql+asyncpg://"
                f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
                f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/"
                f"{os.getenv('DB_NAME')}",
        env="DATABASE_URI",
    )
