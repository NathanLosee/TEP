"""Module providing database interactivity for registered browser operations."""

from typing import Union

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.registered_browser.models import RegisteredBrowser
from src.registered_browser.schemas import RegisteredBrowserBase


def create_registered_browser(
    request: RegisteredBrowserBase,
    db: Session,
) -> RegisteredBrowser:
    """Create a new registered browser.

    Args:
        request (RegisteredBrowserBase): Request data for creating browser.
        db (Session): Database session for the current request.

    Returns:
        RegisteredBrowser: The created registered browser.

    """
    browser = RegisteredBrowser(
        browser_uuid=request.browser_uuid,
        browser_name=request.browser_name,
    )
    db.add(browser)
    db.commit()
    db.refresh(browser)
    return browser


def get_registered_browser_by_uuid(
    browser_uuid: str, db: Session
) -> Union[RegisteredBrowser, None]:
    """Retrieve registered browser by UUID.

    Args:
        browser_uuid (str): Browser's unique UUID.
        db (Session): Database session for the current request.

    Returns:
        Union[RegisteredBrowser, None]: The retrieved browser or None if not
            found.

    """
    return db.scalars(
        select(RegisteredBrowser).where(
            RegisteredBrowser.browser_uuid == browser_uuid
        )
    ).first()


def get_all_registered_browsers(db: Session) -> list[RegisteredBrowser]:
    """Retrieve all registered browsers.

    Args:
        db (Session): Database session for the current request.

    Returns:
        list[RegisteredBrowser]: List of all registered browsers.

    """
    return list(db.scalars(select(RegisteredBrowser)).all())


def delete_registered_browser(browser: RegisteredBrowser, db: Session) -> None:
    """Delete registered browser.

    Args:
        browser (RegisteredBrowser): Browser to be deleted.
        db (Session): Database session for the current request.

    """
    db.delete(browser)
    db.commit()
