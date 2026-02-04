"""Module defining API for license operations."""

import httpx
from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.database import get_db
from src.license.constants import (
    BASE_URL,
    EXC_MSG_INVALID_LICENSE_KEY,
    EXC_MSG_LICENSE_ACTIVATION_FAILED,
    EXC_MSG_LICENSE_NOT_FOUND,
    EXC_MSG_LICENSE_SERVER_ERROR,
    IDENTIFIER,
    LICENSE_SERVER_URL,
)
from src.license.key_generator import (
    get_machine_id,
    normalize_license_key,
    validate_license_key_format,
)
from src.license.repository import (
    create_license as create_license_in_db,
    deactivate_all_licenses,
    deactivate_license as deactivate_license_in_db,
    get_active_license,
    get_license_by_key,
    reactivate_license as reactivate_license_in_db,
)
from src.license.schemas import LicenseActivate, LicenseExtended, LicenseStatus
from src.services import (
    create_event_log,
    get_license_status,
    requires_permission,
    set_license_activated,
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
        requires_permission,
        scopes=["auth_role.create"],  # Only admins
    ),
):
    """Activate a new license.

    Contacts the license server to activate the license for this machine.
    The license server signs the license_key + machine_id to create an
    activation_key that is stored locally.

    Args:
        request (LicenseActivate): License activation data.
        db (Session): Database session for current request.
        caller_badge (str): Badge number of the caller.

    Returns:
        LicenseExtended: The activated license.

    Raises:
        400: If license key format is invalid
        502: If license server is unreachable
        Various: Pass-through errors from license server

    """
    # Validate license key format
    validate(
        validate_license_key_format(request.license_key),
        EXC_MSG_INVALID_LICENSE_KEY,
        status.HTTP_400_BAD_REQUEST,
    )

    # Normalize the license key
    normalized_key = normalize_license_key(request.license_key)

    # Check if this license key already exists locally
    existing_license = get_license_by_key(request.license_key, db)
    if existing_license and existing_license.is_active:
        # Already activated, just return it
        return existing_license

    # Get machine ID for activation
    machine_id = get_machine_id()

    # Track previous state for audit trail
    is_reactivation = existing_license is not None
    previous_license = get_active_license(db)
    previous_key = previous_license.license_key if previous_license else None

    # Contact the license server to activate
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{LICENSE_SERVER_URL}/api/activate",
                json={
                    "license_key": normalized_key,
                    "machine_id": machine_id,
                },
            )
    except httpx.RequestError:
        # Log the server communication failure
        create_event_log(
            IDENTIFIER, "ACTIVATE_SERVER_ERROR", {}, caller_badge, db
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=EXC_MSG_LICENSE_SERVER_ERROR,
        )

    # Handle license server errors
    if response.status_code != 200:
        error_detail = EXC_MSG_LICENSE_ACTIVATION_FAILED
        try:
            error_data = response.json()
            if "detail" in error_data:
                error_detail = error_data["detail"]
        except Exception:
            pass
        # Log the failed activation attempt
        create_event_log(
            IDENTIFIER,
            "ACTIVATE_FAILED",
            {"reason": error_detail},
            caller_badge,
            db,
        )
        raise HTTPException(
            status_code=response.status_code,
            detail=error_detail,
        )

    # Parse response from license server
    activation_data = response.json()
    activation_key = activation_data["activation_key"]

    # Deactivate any existing licenses (only one license can be active)
    deactivate_all_licenses(db)

    # Create or reactivate license locally with the activation key
    try:
        if is_reactivation:
            # Reactivate existing license record
            license_obj = reactivate_license_in_db(
                existing_license, activation_key, db
            )
        else:
            # Create new license record
            license_obj = create_license_in_db(
                normalized_key, activation_key, db
            )
    except IntegrityError:
        # Another concurrent request already created this license
        db.rollback()
        existing = get_license_by_key(normalized_key, db)
        if existing and existing.is_active:
            set_license_activated(True)
            return existing
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="License activation conflict",
        )

    # Update global activation state
    set_license_activated(True)

    # Log with appropriate detail based on context
    if is_reactivation:
        create_event_log(
            IDENTIFIER,
            "REACTIVATE",
            {"license_key": license_obj.license_key},
            caller_badge,
            db,
        )
    elif previous_key and previous_key != license_obj.license_key:
        create_event_log(
            IDENTIFIER,
            "ACTIVATE_REPLACE",
            {
                "license_key": license_obj.license_key,
                "previous_key": previous_key,
            },
            caller_badge,
            db,
        )
    else:
        create_event_log(
            IDENTIFIER,
            "ACTIVATE",
            {"license_key": license_obj.license_key},
            caller_badge,
            db,
        )

    return license_obj


@router.delete(
    "/deactivate",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deactivate_current_license(
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission,
        scopes=["auth_role.delete"],  # Only admins
    ),
):
    """Deactivate the current license.

    Deactivates the local license. Optionally contacts the license server
    to release the activation for potential transfer to another machine.

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

    # Try to deactivate on license server (best effort)
    machine_id = get_machine_id()
    server_notified = True
    try:
        with httpx.Client(timeout=10.0) as client:
            client.post(
                f"{LICENSE_SERVER_URL}/api/deactivate",
                json={
                    "license_key": license_obj.license_key,
                    "machine_id": machine_id,
                },
            )
    except httpx.RequestError:
        # License server unreachable, continue with local deactivation
        server_notified = False

    # Deactivate the license locally
    deactivate_license_in_db(license_obj, db)

    # Update global activation state
    set_license_activated(False)

    # Log with context about whether server was notified
    log_args = {"license_key": license_obj.license_key}
    if server_notified:
        create_event_log(IDENTIFIER, "DEACTIVATE", log_args, caller_badge, db)
    else:
        create_event_log(
            IDENTIFIER, "DEACTIVATE_OFFLINE", log_args, caller_badge, db
        )
