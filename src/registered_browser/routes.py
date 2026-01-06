"""Module defining API for registered browser operations."""

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.orm import Session

import src.registered_browser.repository as browser_repository
from src.database import get_db
from src.registered_browser.constants import (
    BASE_URL,
    EXC_MSG_BROWSER_ALREADY_REGISTERED,
    EXC_MSG_BROWSER_NOT_FOUND,
    IDENTIFIER,
)
from src.registered_browser.models import RegisteredBrowser
from src.registered_browser.schemas import (
    RegisteredBrowserBase,
    RegisteredBrowserExtended,
)
from src.services import create_event_log, requires_permission, validate

router = APIRouter(prefix=BASE_URL, tags=["registered_browsers"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisteredBrowserExtended,
)
def register_browser(
    request: RegisteredBrowserBase,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["registered_browser.create"]
    ),
):
    """Register a new browser.

    Args:
        request (RegisteredBrowserBase): Request data for registering browser.
        db (Session): Database session for current request.

    Returns:
        RegisteredBrowserExtended: The created registered browser.

    """
    existing_browser = browser_repository.get_registered_browser_by_uuid(
        request.browser_uuid, db
    )
    validate(
        not existing_browser,
        EXC_MSG_BROWSER_ALREADY_REGISTERED,
        status.HTTP_409_CONFLICT,
    )

    browser = browser_repository.create_registered_browser(request, db)
    log_args = {
        "browser_id": browser.id,
        "browser_uuid": browser.browser_uuid,
    }
    create_event_log(IDENTIFIER, "CREATE", log_args, caller_badge, db)
    return browser


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
    return browser_repository.get_all_registered_browsers(db)


@router.delete(
    "/{browser_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_registered_browser(
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

    browser_repository.delete_registered_browser(browser, db)
    log_args = {"browser_id": browser_id, "browser_uuid": browser.browser_uuid}
    create_event_log(IDENTIFIER, "DELETE", log_args, caller_badge, db)
