"""Module providing application configuration settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    Attributes:
        LOG_LEVEL (str): The log level.
        POSTGRES_USER (str): The postgres user.
        POSTGRES_PASSWORD (str): The postgres password.
        POSTGRES_DB (str): The postgres database.
        POSTGRES_HOST (str): The postgres host.
        POSTGRES_PORT (str): The postgres port.

    """

    LOG_LEVEL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    model_config = SettingsConfigDict(env_file="../.env")


@lru_cache()
def get_settings() -> Settings:
    """Return the application settings.

    Returns:
        Settings: The application settings.

    """
    return Settings()
