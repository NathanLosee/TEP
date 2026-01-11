"""Module providing database interactivity for registered browser operations."""

from datetime import datetime
from typing import Union

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.registered_browser.models import RegisteredBrowser
from src.registered_browser.schemas import RegisteredBrowserCreate


def create_registered_browser(
    request: RegisteredBrowserCreate,
    db: Session,
) -> RegisteredBrowser:
    """Create a new registered browser.

    Args:
        request (RegisteredBrowserCreate): Request data for creating browser.
        db (Session): Database session for the current request.

    Returns:
        RegisteredBrowser: The created registered browser.

    """
    browser = RegisteredBrowser(
        browser_uuid=request.browser_uuid,
        browser_name=request.browser_name,
        fingerprint_hash=request.fingerprint_hash,
        user_agent=request.user_agent,
        ip_address=request.ip_address,
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


def get_registered_browser_by_name(
    browser_name: str, db: Session
) -> Union[RegisteredBrowser, None]:
    """Retrieve registered browser by name.

    Args:
        browser_name (str): Browser's friendly name.
        db (Session): Database session for the current request.

    Returns:
        Union[RegisteredBrowser, None]: The retrieved browser or None if not found.

    """
    return db.scalars(
        select(RegisteredBrowser).where(
            RegisteredBrowser.browser_name == browser_name
        )
    ).first()


def get_registered_browser_by_fingerprint(
    fingerprint_hash: str, db: Session
) -> Union[RegisteredBrowser, None]:
    """Retrieve registered browser by fingerprint hash.

    Args:
        fingerprint_hash (str): Browser's fingerprint hash.
        db (Session): Database session for the current request.

    Returns:
        Union[RegisteredBrowser, None]: The retrieved browser or None if not found.

    """
    return db.scalars(
        select(RegisteredBrowser).where(
            RegisteredBrowser.fingerprint_hash == fingerprint_hash,
            RegisteredBrowser.is_active == True,
        )
    ).first()


def update_browser_last_seen(browser: RegisteredBrowser, db: Session) -> None:
    """Update the last_seen timestamp for a browser.

    Args:
        browser (RegisteredBrowser): Browser to update.
        db (Session): Database session for the current request.

    """
    browser.last_seen = datetime.now()
    db.add(browser)
    db.commit()


def delete_registered_browser(browser: RegisteredBrowser, db: Session) -> None:
    """Delete registered browser.

    Args:
        browser (RegisteredBrowser): Browser to be deleted.
        db (Session): Database session for the current request.

    """
    db.delete(browser)
    db.commit()


def get_all_browser_uuids(db: Session) -> set[str]:
    """Get all existing browser UUIDs.

    Args:
        db (Session): Database session for the current request.

    Returns:
        set[str]: Set of all browser UUIDs currently in the database.

    """
    browsers = db.scalars(select(RegisteredBrowser.browser_uuid)).all()
    return set(browsers)


def update_browser_fingerprint(
    browser: RegisteredBrowser, fingerprint_hash: str, db: Session
) -> None:
    """Update the fingerprint hash for a browser during recovery.

    Args:
        browser (RegisteredBrowser): Browser to update.
        fingerprint_hash (str): New fingerprint hash.
        db (Session): Database session for the current request.

    """
    browser.fingerprint_hash = fingerprint_hash
    browser.last_seen = datetime.now()
    db.add(browser)
    db.commit()


def start_active_session(
    browser: RegisteredBrowser, fingerprint_hash: str, db: Session
) -> None:
    """Start an active session for a browser.

    Args:
        browser (RegisteredBrowser): Browser to start session for.
        fingerprint_hash (str): Fingerprint hash of the active session.
        db (Session): Database session for the current request.

    """
    browser.active_session_fingerprint = fingerprint_hash
    browser.active_session_started = datetime.now()
    browser.last_seen = datetime.now()
    db.add(browser)
    db.commit()


def clear_active_session(browser: RegisteredBrowser, db: Session) -> None:
    """Clear the active session for a browser.

    Args:
        browser (RegisteredBrowser): Browser to clear session for.
        db (Session): Database session for the current request.

    """
    browser.active_session_fingerprint = None
    browser.active_session_started = None
    db.add(browser)
    db.commit()


def has_active_session_conflict(
    browser: RegisteredBrowser, fingerprint_hash: str
) -> bool:
    """Check if browser has an active session with a different fingerprint.

    Args:
        browser (RegisteredBrowser): Browser to check.
        fingerprint_hash (str): Fingerprint hash to compare against.

    Returns:
        bool: True if there's an active session with a different fingerprint.

    """
    # No active session means no conflict
    if not browser.active_session_fingerprint:
        return False

    # Same fingerprint means no conflict (same browser)
    if browser.active_session_fingerprint == fingerprint_hash:
        return False

    # Different fingerprint means there's a conflict
    return True


def clear_stale_sessions(db: Session, timeout_minutes: int = 30) -> None:
    """Clear sessions that haven't been seen recently.

    Args:
        db (Session): Database session for the current request.
        timeout_minutes (int): Minutes of inactivity before session is stale.

    """
    from datetime import timedelta

    cutoff_time = datetime.now() - timedelta(minutes=timeout_minutes)

    browsers = db.scalars(
        select(RegisteredBrowser).where(
            RegisteredBrowser.active_session_started.isnot(None),
            RegisteredBrowser.last_seen < cutoff_time,
        )
    ).all()

    for browser in browsers:
        browser.active_session_fingerprint = None
        browser.active_session_started = None
        db.add(browser)

    db.commit()
