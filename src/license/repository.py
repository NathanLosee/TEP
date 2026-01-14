"""Module providing database interactivity for license operations."""

from typing import Union

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.license.models import License
from src.license.schemas import LicenseActivate


def get_active_license(db: Session) -> Union[License, None]:
    """Retrieve the active license.

    Args:
        db (Session): Database session for the current request.

    Returns:
        Union[License, None]: The active license or None if no license exists.

    """
    return db.scalars(
        select(License).where(License.is_active == True)
    ).first()


def get_license_by_key(
    license_key: str, db: Session
) -> Union[License, None]:
    """Retrieve license by key.

    Args:
        license_key (str): The license key.
        db (Session): Database session for the current request.

    Returns:
        Union[License, None]: The retrieved license or None if not found.

    """
    return db.scalars(
        select(License).where(License.license_key == license_key)
    ).first()


def create_license(request: LicenseActivate, db: Session) -> License:
    """Create a new license.

    Args:
        request (LicenseActivate): Request data for activating license.
        db (Session): Database session for the current request.

    Returns:
        License: The created license.

    """
    license_obj = License(
        license_key=request.license_key,
        server_id=request.server_id,
        is_active=True,
    )
    db.add(license_obj)
    db.commit()
    db.refresh(license_obj)
    return license_obj


def deactivate_license(license_obj: License, db: Session) -> None:
    """Deactivate a license.

    Args:
        license_obj (License): License to deactivate.
        db (Session): Database session for the current request.

    """
    license_obj.is_active = False
    db.add(license_obj)
    db.commit()


def deactivate_all_licenses(db: Session) -> None:
    """Deactivate all licenses (used before activating a new one).

    Args:
        db (Session): Database session for the current request.

    """
    licenses = db.scalars(select(License).where(License.is_active == True)).all()
    for license_obj in licenses:
        license_obj.is_active = False
        db.add(license_obj)
    db.commit()
