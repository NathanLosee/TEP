"""Module providing database interactivity for license operations."""

from typing import Union

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.license.key_generator import normalize_license_key
from src.license.models import License


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
        license_key (str): The license key (word or hex format).
        db (Session): Database session for the current request.

    Returns:
        Union[License, None]: The retrieved license or None if not found.

    """
    # Normalize the key to hex format for comparison
    normalized_key = normalize_license_key(license_key)
    return db.scalars(
        select(License).where(License.license_key == normalized_key)
    ).first()


def create_license(
    license_key: str, activation_key: str, db: Session
) -> License:
    """Create a new license with activation key.

    Args:
        license_key (str): The license key (already normalized to hex).
        activation_key (str): The activation key from license server.
        db (Session): Database session for the current request.

    Returns:
        License: The created license.

    """
    license_obj = License(
        license_key=license_key,
        activation_key=activation_key,
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


def reactivate_license(
    license_obj: License, activation_key: str, db: Session
) -> License:
    """Reactivate an existing license with a new activation key.

    Used when reactivating a license that was previously deactivated.

    Args:
        license_obj (License): Existing license to reactivate.
        activation_key (str): The new activation key from license server.
        db (Session): Database session for the current request.

    Returns:
        License: The reactivated license.

    """
    license_obj.activation_key = activation_key
    license_obj.is_active = True
    db.add(license_obj)
    db.commit()
    db.refresh(license_obj)
    return license_obj


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
