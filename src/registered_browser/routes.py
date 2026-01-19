"""Module defining API for registered browser operations."""

from fastapi import APIRouter, Depends, Request, Security, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.registered_browser.constants import (
    BASE_URL,
    EXC_MSG_BROWSER_ALREADY_REGISTERED,
    EXC_MSG_BROWSER_NAME_ALREADY_EXISTS,
    EXC_MSG_BROWSER_NOT_FOUND,
    IDENTIFIER,
)
from src.registered_browser.models import RegisteredBrowser
from src.registered_browser.repository import (
    clear_stale_sessions,
    create_registered_browser as create_registered_browser_in_db,
    delete_registered_browser as delete_registered_browser_from_db,
    get_all_browser_uuids,
    get_all_registered_browsers,
    get_registered_browser_by_fingerprint,
    get_registered_browser_by_name,
    get_registered_browser_by_uuid,
    has_active_session_conflict,
    start_active_session,
    update_browser_fingerprint,
)
from src.registered_browser.schemas import (
    RegisteredBrowserCreate,
    RegisteredBrowserExtended,
    RegisteredBrowserRecover,
    RegisteredBrowserVerify,
)
from src.registered_browser.uuid_generator import (
    generate_unique_uuid,
    validate_uuid_format,
)
from src.services import create_event_log, requires_license, requires_permission, validate

router = APIRouter(prefix=BASE_URL, tags=["registered_browsers"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisteredBrowserExtended,
)
def register_browser(
    request: RegisteredBrowserCreate,
    http_request: Request,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["registered_browser.create"]
    ),
):
    """Register a new browser.

    Args:
        request (RegisteredBrowserCreate): Request data for registering browser.
        http_request (Request): FastAPI request object for IP address.
        db (Session): Database session for current request.
        caller_badge (str): Badge number of the caller.

    Returns:
        RegisteredBrowserExtended: The created registered browser.

    """
    # Generate UUID if not provided, using human-readable format
    if not request.browser_uuid:
        existing_uuids = get_all_browser_uuids(db)
        request.browser_uuid = generate_unique_uuid(existing_uuids)
    else:
        # Validate UUID format if provided
        validate(
            validate_uuid_format(request.browser_uuid),
            "Invalid UUID format. Expected format: WORD-WORD-WORD-NUMBER",
            status.HTTP_400_BAD_REQUEST,
        )
        # Check if UUID already exists
        existing_browser_uuid = get_registered_browser_by_uuid(
            request.browser_uuid, db
        )
        validate(
            not existing_browser_uuid,
            EXC_MSG_BROWSER_ALREADY_REGISTERED,
            status.HTTP_409_CONFLICT,
        )

    # Check if browser name already exists
    existing_browser_name = get_registered_browser_by_name(
        request.browser_name, db
    )
    validate(
        not existing_browser_name,
        EXC_MSG_BROWSER_NAME_ALREADY_EXISTS,
        status.HTTP_409_CONFLICT,
    )

    # Set IP address from request if not provided
    if not request.ip_address:
        request.ip_address = http_request.client.host if http_request.client else None

    browser = create_registered_browser_in_db(request, db)
    log_args = {
        "browser_id": browser.id,
        "browser_uuid": browser.browser_uuid,
        "browser_name": browser.browser_name,
    }
    create_event_log(IDENTIFIER, "CREATE", log_args, caller_badge, db)
    return browser


@router.post(
    "/verify",
    status_code=status.HTTP_200_OK,
)
def verify_browser(
    request: RegisteredBrowserVerify,
    db: Session = Depends(get_db),
):
    """Verify browser fingerprint and return UUID if match found.

    Args:
        request (RegisteredBrowserVerify): Verification request with fingerprint.
        db (Session): Database session for current request.

    Returns:
        dict: Contains browser_uuid if match found, or None if no match.

    """
    # Clear any stale sessions before processing
    clear_stale_sessions(db)

    # First check if provided UUID exists and is active
    if request.browser_uuid:
        browser_by_uuid = get_registered_browser_by_uuid(
            request.browser_uuid, db
        )
        if browser_by_uuid and browser_by_uuid.is_active:
            # Start or update active session
            start_active_session(browser_by_uuid, request.fingerprint_hash, db)
            return {
                "browser_uuid": browser_by_uuid.browser_uuid,
                "browser_name": browser_by_uuid.browser_name,
                "verified": True,
            }

    # Try to find by fingerprint
    browser_by_fingerprint = get_registered_browser_by_fingerprint(
        request.fingerprint_hash, db
    )

    if browser_by_fingerprint:
        # Start or update active session
        start_active_session(
            browser_by_fingerprint, request.fingerprint_hash, db
        )
        return {
            "browser_uuid": browser_by_fingerprint.browser_uuid,
            "browser_name": browser_by_fingerprint.browser_name,
            "verified": True,
            "restored": True,  # Indicates UUID was restored from fingerprint
        }

    # No match found
    return {"browser_uuid": None, "verified": False}


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[RegisteredBrowserExtended],
)
def get_registered_browsers(
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["registered_browser.read"]
    ),
):
    """Retrieve all registered browsers.

    Args:
        db (Session): Database session for current request.
        caller_badge (str): Badge number of the caller.

    Returns:
        list[RegisteredBrowserExtended]: List of all registered browsers.

    """
    return get_all_registered_browsers(db)


@router.delete(
    "/{browser_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_browser(
    browser_id: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["registered_browser.delete"]
    ),
):
    """Delete a registered browser.

    Args:
        browser_id (int): Browser's unique identifier.
        db (Session): Database session for current request.

    """
    browser = db.get(RegisteredBrowser, browser_id)
    validate(
        browser,
        EXC_MSG_BROWSER_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    delete_registered_browser_from_db(browser, db)
    log_args = {"browser_id": browser_id, "browser_uuid": browser.browser_uuid}
    create_event_log(IDENTIFIER, "DELETE", log_args, caller_badge, db)


@router.post(
    "/recover",
    status_code=status.HTTP_200_OK,
)
def recover_browser(
    request: RegisteredBrowserRecover,
    db: Session = Depends(get_db),
):
    """Recover browser registration using device ID (UUID).

    This allows an employee to recover their device registration if localStorage
    was cleared. The device ID is the device UUID in human-readable format.

    Args:
        request (RegisteredBrowserRecover): Recovery request with code and fingerprint.
        db (Session): Database session for current request.

    Returns:
        dict: Contains browser_uuid and browser_name if recovery successful.

    Raises:
        400: If device ID format is invalid
        404: If device ID not found or browser is inactive
        409: If device ID is already in use by another active session

    """
    # Clear any stale sessions before processing
    clear_stale_sessions(db)

    # Validate device ID format
    validate(
        validate_uuid_format(request.recovery_code),
        "Invalid device ID format. Expected format: WORD-WORD-WORD-NUMBER",
        status.HTTP_400_BAD_REQUEST,
    )

    # Find browser by device ID (which is the UUID)
    browser = get_registered_browser_by_uuid(request.recovery_code, db)

    validate(
        browser and browser.is_active,
        "Device ID not found or browser is inactive",
        status.HTTP_404_NOT_FOUND,
    )

    # Check if this device ID has an active session with a different fingerprint
    validate(
        not has_active_session_conflict(browser, request.fingerprint_hash),
        "This device ID is currently in use by another browser. Please wait a few minutes and try again, or contact an administrator if the device is no longer in use.",
        status.HTTP_409_CONFLICT,
    )

    # Update browser fingerprint to current device
    update_browser_fingerprint(browser, request.fingerprint_hash, db)

    # Start active session for this browser
    start_active_session(browser, request.fingerprint_hash, db)

    # Note: Event logging is skipped for recovery since this is an unauthenticated
    # endpoint and there's no valid badge_number to associate with the log entry.
    # Recovery is already tracked through the active_session_started timestamp.

    return {
        "browser_uuid": browser.browser_uuid,
        "browser_name": browser.browser_name,
        "recovered": True,
    }
