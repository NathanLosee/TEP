"""Module defining API for license operations."""

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.license.constants import (
    BASE_URL,
    EXC_MSG_INVALID_LICENSE_KEY,
    EXC_MSG_LICENSE_ALREADY_ACTIVATED,
    EXC_MSG_LICENSE_NOT_FOUND,
    IDENTIFIER,
)
from src.license.key_generator import (
    validate_license_key_format,
    verify_license_key,
)
from src.license.models import License
from src.license.repository import (
    create_license as create_license_in_db,
    deactivate_all_licenses,
    deactivate_license as deactivate_license_in_db,
    get_active_license,
    get_license_by_key,
)
from src.license.schemas import LicenseActivate, LicenseExtended, LicenseStatus
from src.services import (
    create_event_log,
    get_license_status,
    requires_permission,
    validate,
)

router = APIRouter(prefix=BASE_URL, tags=["licenses"])


@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    response_model=LicenseStatus,
)
def check_license_status(
    db: Session = Depends(get_db),
):
    """Get current license status.

    This endpoint is publicly accessible (no authentication required)
    so that the frontend can check license status before login.

    Args:
        db (Session): Database session for current request.

    Returns:
        LicenseStatus: Current license status.

    """
    return get_license_status(db)


@router.post(
    "/activate",
    status_code=status.HTTP_201_CREATED,
    response_model=LicenseExtended,
)
def activate_license(
    request: LicenseActivate,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["auth_role.create"]  # Only admins can activate
    ),
):
    """Activate a new license.

    Validates the license key format and cryptographic signature,
    deactivates any existing licenses, and activates the new one.

    Args:
        request (LicenseActivate): License activation data.
        db (Session): Database session for current request.
        caller_badge (str): Badge number of the caller.

    Returns:
        LicenseExtended: The activated license.

    Raises:
        400: If license key format is invalid or signature verification fails
        409: If license key is already activated

    """
    # Validate license key format
    validate(
        validate_license_key_format(request.license_key),
        EXC_MSG_INVALID_LICENSE_KEY,
        status.HTTP_400_BAD_REQUEST,
    )

    # Verify cryptographic signature
    validate(
        verify_license_key(request.license_key),
        EXC_MSG_INVALID_LICENSE_KEY,
        status.HTTP_400_BAD_REQUEST,
    )

    # Check if this license key already exists
    existing_license = get_license_by_key(request.license_key, db)
    validate(
        not existing_license,
        EXC_MSG_LICENSE_ALREADY_ACTIVATED,
        status.HTTP_409_CONFLICT,
    )

    # Deactivate any existing licenses (only one license can be active)
    deactivate_all_licenses(db)

    # Create new license
    license_obj = create_license_in_db(request, db)

    # Log the activation
    log_args = {
        "license_key": license_obj.license_key,
    }
    create_event_log(IDENTIFIER, "ACTIVATE", log_args, caller_badge, db)

    return license_obj


@router.delete(
    "/deactivate",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deactivate_current_license(
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["auth_role.delete"]  # Only admins can deactivate
    ),
):
    """Deactivate the current license.

    Args:
        db (Session): Database session for current request.
        caller_badge (str): Badge number of the caller.

    Raises:
        404: If no active license exists

    """
    license_obj = get_active_license(db)
    validate(
        license_obj,
        EXC_MSG_LICENSE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    # Deactivate the license
    deactivate_license_in_db(license_obj, db)

    # Log the deactivation
    log_args = {
        "license_key": license_obj.license_key,
    }
    create_event_log(IDENTIFIER, "DEACTIVATE", log_args, caller_badge, db)
