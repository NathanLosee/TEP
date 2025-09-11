"""Module providing application configuration settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    Attributes:
        LOG_LEVEL (str): The log level.
        ENVIRONMENT (str): The environment in which the application is running.
        DATABASE_URL (str): The database URL.

    """

    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = ""

    def get_database_url(self) -> str:
        """Get the database URL based on environment.
        
        Returns:
            str: The appropriate database URL for the current environment.
        """
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        if self.ENVIRONMENT.lower() == "production":
            return "sqlite:///tep_prod.sqlite"
        else:
            return "sqlite:///tep_dev.sqlite"

    model_config = SettingsConfigDict(env_file="../.env")
