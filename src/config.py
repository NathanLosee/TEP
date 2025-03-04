"""Module providing application configuration settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    Attributes:
        LOG_LEVEL (str): The log level.

    """

    LOG_LEVEL: str

    model_config = SettingsConfigDict(env_file="../.env")


@lru_cache()
def get_settings() -> Settings:
    """Return the application settings.

    Returns:
        Settings: The application settings.

    """
    return Settings()
