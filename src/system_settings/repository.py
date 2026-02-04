"""Repository functions for system settings database operations."""

from typing import Optional, Tuple

from sqlalchemy.orm import Session

from src.system_settings.models import SystemSettings
from src.system_settings.schemas import SystemSettingsUpdate


def get_settings(db: Session) -> SystemSettings:
    """Get system settings (creates default if not exists).

    Args:
        db: Database session.

    Returns:
        SystemSettings: The system settings object.

    """
    settings = db.get(SystemSettings, 1)
    if not settings:
        # Create default settings
        settings = SystemSettings(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def update_settings(
    settings: SystemSettings,
    request: SystemSettingsUpdate,
    db: Session,
) -> SystemSettings:
    """Update system settings.

    Args:
        settings: Current settings object.
        request: Update request data.
        db: Database session.

    Returns:
        SystemSettings: Updated settings object.

    """
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(settings, field, value)
    db.commit()
    db.refresh(settings)
    return settings


def update_logo(
    settings: SystemSettings,
    logo_data: bytes,
    mime_type: str,
    filename: str,
    db: Session,
) -> SystemSettings:
    """Update the logo in system settings.

    Args:
        settings: Current settings object.
        logo_data: Binary logo data.
        mime_type: MIME type of the logo.
        filename: Original filename.
        db: Database session.

    Returns:
        SystemSettings: Updated settings object.

    """
    settings.logo_data = logo_data
    settings.logo_mime_type = mime_type
    settings.logo_filename = filename
    db.commit()
    db.refresh(settings)
    return settings


def delete_logo(settings: SystemSettings, db: Session) -> SystemSettings:
    """Delete the logo from system settings.

    Args:
        settings: Current settings object.
        db: Database session.

    Returns:
        SystemSettings: Updated settings object.

    """
    settings.logo_data = None
    settings.logo_mime_type = None
    settings.logo_filename = None
    db.commit()
    db.refresh(settings)
    return settings


def get_logo(db: Session) -> Optional[Tuple[bytes, str, str]]:
    """Get logo data if exists.

    Args:
        db: Database session.

    Returns:
        Optional tuple of (logo_data, mime_type, filename) or None.

    """
    settings = get_settings(db)
    if settings.logo_data:
        return (
            settings.logo_data,
            settings.logo_mime_type,
            settings.logo_filename,
        )
    return None
