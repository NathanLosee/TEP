"""Module providing application configuration settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    Attributes:
        LOG_LEVEL (str): The log level.
        ENVIRONMENT (str): The environment in which the application is running.

    """

    LOG_LEVEL: str
    ENVIRONMENT: str

    model_config = SettingsConfigDict(env_file="../.env")
