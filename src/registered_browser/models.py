"""Module for defining registered browser data models.

Classes:
    - RegisteredBrowser: SQLAlchemy model for the
        'registered_browsers' table in the database.

"""

from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base
from src.registered_browser.constants import IDENTIFIER


class RegisteredBrowser(Base):
    """SQLAlchemy model for registered browser data.

    Attributes:
        id (int): Browser's unique identifier.
        browser_uuid (str): Browser's unique UUID.
        browser_name (str): Browser's friendly name (unique).
        fingerprint_hash (str): Hash of browser fingerprint for verification.
        user_agent (str): Browser user agent string.
        ip_address (str): IP address at registration time.
        registered_at (datetime): When the browser was registered.
        last_seen (datetime): Last time the browser was used.
        is_active (bool): Whether the browser is currently active.
        active_session_fingerprint (str): Fingerprint of
            currently active session.
        active_session_started (datetime): When current session started.

    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    browser_uuid: Mapped[str] = mapped_column(unique=True, nullable=False)
    browser_name: Mapped[str] = mapped_column(unique=True, nullable=False)
    fingerprint_hash: Mapped[Optional[str]] = mapped_column(
        nullable=True, index=True,
    )
    user_agent: Mapped[Optional[str]] = mapped_column(nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(nullable=True)
    registered_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    last_seen: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(),
        onupdate=func.now(), index=True,
    )
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    active_session_fingerprint: Mapped[Optional[str]] = (
        mapped_column(nullable=True)
    )
    active_session_started: Mapped[Optional[datetime]] = (
        mapped_column(nullable=True)
    )

    __tablename__ = IDENTIFIER
