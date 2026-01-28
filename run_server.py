#!/usr/bin/env python3
"""Entry point for running TEP backend server.

This script serves as the entry point for the PyInstaller-bundled executable.
It starts the FastAPI application using uvicorn.

Usage:
    python run_server.py
    # Or after PyInstaller build:
    ./tep.exe
"""

import os
import sys
from pathlib import Path

# Load .env file early before any other imports
# This ensures environment variables are available for all modules


def _load_dotenv():
    """Load .env file from the appropriate location."""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle - .env is next to executable
        env_path = Path(sys.executable).parent / ".env"
    else:
        # Running from source - .env is in project root
        env_path = Path(__file__).parent / ".env"

    if env_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
            print(f"Loaded environment from: {env_path}")
        except ImportError:
            # Fallback: manually parse .env file
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()


def get_base_path() -> Path:
    """Get the base path for the application.

    When running as a PyInstaller bundle, sys._MEIPASS contains the path
    to the extracted bundle. Otherwise, use the current directory.

    Returns:
        Path: Base path for the application.
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        return Path(sys._MEIPASS)
    else:
        # Running as script
        return Path(__file__).parent


def init_database():
    """Initialize the database for production.

    This creates all tables using SQLAlchemy if they don't exist.
    In PyInstaller bundles, running alembic migrations is complex,
    so we use create_all() for initial setup.
    """
    print("Initializing database...")
    try:
        from src.database import engine, Base

        # Import all models to register them with Base.metadata
        from src.auth_role import models as auth_role_models
        from src.department import models as department_models
        from src.employee import models as employee_models
        from src.event_log import models as event_log_models
        from src.holiday_group import models as holiday_group_models
        from src.license import models as license_models
        from src.org_unit import models as org_unit_models
        from src.registered_browser import models as registered_browser_models
        from src.system_settings import models as system_settings_models
        from src.timeclock import models as timeclock_models
        from src.user import models as user_models

        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully.")
        return True
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False


def main():
    """Main entry point for the TEP server."""
    import uvicorn
    from src.config import Settings

    settings = Settings()

    # Get port from environment or default (Settings doesn't have BACKEND_PORT)
    port = int(os.environ.get('BACKEND_PORT', 8000))
    host = os.environ.get('BACKEND_HOST', '0.0.0.0')

    print("=" * 60)
    print("TEP - Timeclock and Employee Payroll")
    print("=" * 60)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Starting server on {host}:{port}")
    print("=" * 60)

    # Run migrations before starting (production mode)
    if settings.ENVIRONMENT != "development":
        if not init_database():
            print("Warning: Database initialization failed.")

    # Run the server
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=False,  # Disable reload for production
        log_level=settings.LOG_LEVEL.lower() if settings.LOG_LEVEL else "info",
    )


if __name__ == "__main__":
    main()
