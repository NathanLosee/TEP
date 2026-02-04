"""Unit tests for registered_browser repository."""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.registered_browser.models import RegisteredBrowser
from src.registered_browser.repository import (
    clear_active_session,
    clear_stale_sessions,
    has_active_session_conflict,
    start_active_session,
)

TEST_DB_URL = "sqlite:///tap_unit_test_browser.sqlite"
engine = create_engine(TEST_DB_URL)
TestSession = sessionmaker(bind=engine)


@pytest.fixture
def db():
    """Provide a clean database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def _make_browser(
    browser_uuid="uuid-1",
    browser_name="Browser 1",
    fingerprint_hash=None,
    active_session_fingerprint=None,
    active_session_started=None,
    last_seen=None,
):
    """Create a RegisteredBrowser instance for testing.

    Args:
        browser_uuid: Unique browser identifier.
        browser_name: Human-readable browser name.
        fingerprint_hash: Hash of browser fingerprint.
        active_session_fingerprint: Fingerprint of active session.
        active_session_started: When the active session began.
        last_seen: Last time this browser was seen.

    Returns:
        RegisteredBrowser: A new browser model instance.

    """
    return RegisteredBrowser(
        browser_uuid=browser_uuid,
        browser_name=browser_name,
        fingerprint_hash=fingerprint_hash,
        active_session_fingerprint=active_session_fingerprint,
        active_session_started=active_session_started,
        last_seen=last_seen or datetime.now(),
    )


class TestHasActiveSessionConflict:
    """Tests for has_active_session_conflict (pure logic)."""

    def test_no_active_session_returns_false(self):
        """No conflict when browser has no active session."""
        browser = _make_browser(
            active_session_fingerprint=None,
        )
        result = has_active_session_conflict(
            browser, "some-fingerprint"
        )
        assert result is False

    def test_same_fingerprint_returns_false(self):
        """No conflict when fingerprint matches active session."""
        fp = "matching-fingerprint"
        browser = _make_browser(
            active_session_fingerprint=fp,
        )
        result = has_active_session_conflict(browser, fp)
        assert result is False

    def test_different_fingerprint_returns_true(self):
        """Conflict when fingerprint differs from active session."""
        browser = _make_browser(
            active_session_fingerprint="fingerprint-A",
        )
        result = has_active_session_conflict(
            browser, "fingerprint-B"
        )
        assert result is True

    def test_empty_string_session_returns_false(self):
        """Empty string active session is falsy, so no conflict."""
        browser = _make_browser(
            active_session_fingerprint="",
        )
        result = has_active_session_conflict(
            browser, "some-fingerprint"
        )
        assert result is False


class TestClearStaleSessions:
    """Tests for clear_stale_sessions (requires DB)."""

    def test_clears_sessions_older_than_timeout(self, db):
        """Sessions older than timeout should be cleared."""
        stale_time = datetime.now() - timedelta(minutes=45)
        browser = _make_browser(
            active_session_fingerprint="fp-stale",
            active_session_started=stale_time,
            last_seen=stale_time,
        )
        db.add(browser)
        db.commit()

        clear_stale_sessions(db, timeout_minutes=30)

        db.refresh(browser)
        assert browser.active_session_fingerprint is None
        assert browser.active_session_started is None

    def test_keeps_sessions_within_timeout(self, db):
        """Sessions within the timeout window should be kept."""
        recent_time = datetime.now() - timedelta(minutes=10)
        browser = _make_browser(
            active_session_fingerprint="fp-recent",
            active_session_started=recent_time,
            last_seen=recent_time,
        )
        db.add(browser)
        db.commit()

        clear_stale_sessions(db, timeout_minutes=30)

        db.refresh(browser)
        assert browser.active_session_fingerprint == "fp-recent"
        assert browser.active_session_started is not None

    def test_handles_no_stale_sessions(self, db):
        """Should succeed when there are no stale sessions."""
        recent_time = datetime.now() - timedelta(minutes=5)
        browser = _make_browser(
            active_session_fingerprint="fp-active",
            active_session_started=recent_time,
            last_seen=recent_time,
        )
        db.add(browser)
        db.commit()

        clear_stale_sessions(db, timeout_minutes=30)

        db.refresh(browser)
        assert browser.active_session_fingerprint == "fp-active"

    def test_handles_empty_database(self, db):
        """Should succeed when the database has no browsers."""
        clear_stale_sessions(db, timeout_minutes=30)

    def test_clears_only_stale_sessions(self, db):
        """Only stale sessions are cleared; fresh ones are kept."""
        stale_time = datetime.now() - timedelta(minutes=60)
        fresh_time = datetime.now() - timedelta(minutes=5)

        stale_browser = _make_browser(
            browser_uuid="uuid-stale",
            browser_name="Stale Browser",
            active_session_fingerprint="fp-stale",
            active_session_started=stale_time,
            last_seen=stale_time,
        )
        fresh_browser = _make_browser(
            browser_uuid="uuid-fresh",
            browser_name="Fresh Browser",
            active_session_fingerprint="fp-fresh",
            active_session_started=fresh_time,
            last_seen=fresh_time,
        )
        db.add_all([stale_browser, fresh_browser])
        db.commit()

        clear_stale_sessions(db, timeout_minutes=30)

        db.refresh(stale_browser)
        db.refresh(fresh_browser)
        assert stale_browser.active_session_fingerprint is None
        assert stale_browser.active_session_started is None
        assert fresh_browser.active_session_fingerprint == "fp-fresh"
        assert fresh_browser.active_session_started is not None

    def test_ignores_browsers_without_active_session(self, db):
        """Browsers with no active session should be untouched."""
        old_time = datetime.now() - timedelta(minutes=60)
        browser = _make_browser(
            active_session_fingerprint=None,
            active_session_started=None,
            last_seen=old_time,
        )
        db.add(browser)
        db.commit()

        clear_stale_sessions(db, timeout_minutes=30)

        db.refresh(browser)
        assert browser.active_session_fingerprint is None
        assert browser.active_session_started is None

    def test_custom_timeout_value(self, db):
        """Custom timeout of 10 minutes should clear 15-min-old."""
        old_time = datetime.now() - timedelta(minutes=15)
        browser = _make_browser(
            active_session_fingerprint="fp-old",
            active_session_started=old_time,
            last_seen=old_time,
        )
        db.add(browser)
        db.commit()

        clear_stale_sessions(db, timeout_minutes=10)

        db.refresh(browser)
        assert browser.active_session_fingerprint is None
        assert browser.active_session_started is None


class TestStartActiveSession:
    """Tests for start_active_session (requires DB)."""

    def test_sets_session_fields(self, db):
        """Should set fingerprint, started, and last_seen."""
        browser = _make_browser()
        db.add(browser)
        db.commit()

        before = datetime.now()
        start_active_session(browser, "fp-new", db)
        after = datetime.now()

        db.refresh(browser)
        assert browser.active_session_fingerprint == "fp-new"
        assert browser.active_session_started is not None
        assert before <= browser.active_session_started <= after
        assert before <= browser.last_seen <= after

    def test_persists_to_database(self, db):
        """Session data should persist after commit."""
        browser = _make_browser()
        db.add(browser)
        db.commit()
        browser_id = browser.id

        start_active_session(browser, "fp-persist", db)

        fetched = db.get(RegisteredBrowser, browser_id)
        assert fetched.active_session_fingerprint == "fp-persist"
        assert fetched.active_session_started is not None

    def test_overwrites_existing_session(self, db):
        """Starting a new session should overwrite the old one."""
        browser = _make_browser(
            active_session_fingerprint="fp-old",
            active_session_started=(
                datetime.now() - timedelta(hours=1)
            ),
        )
        db.add(browser)
        db.commit()

        start_active_session(browser, "fp-new", db)

        db.refresh(browser)
        assert browser.active_session_fingerprint == "fp-new"


class TestClearActiveSession:
    """Tests for clear_active_session (requires DB)."""

    def test_clears_session_fields(self, db):
        """Should set fingerprint and started to None."""
        browser = _make_browser(
            active_session_fingerprint="fp-active",
            active_session_started=datetime.now(),
        )
        db.add(browser)
        db.commit()

        clear_active_session(browser, db)

        db.refresh(browser)
        assert browser.active_session_fingerprint is None
        assert browser.active_session_started is None

    def test_persists_to_database(self, db):
        """Cleared session should persist after commit."""
        browser = _make_browser(
            active_session_fingerprint="fp-to-clear",
            active_session_started=datetime.now(),
        )
        db.add(browser)
        db.commit()
        browser_id = browser.id

        clear_active_session(browser, db)

        fetched = db.get(RegisteredBrowser, browser_id)
        assert fetched.active_session_fingerprint is None
        assert fetched.active_session_started is None

    def test_clearing_already_empty_session(self, db):
        """Clearing a browser with no active session should succeed."""
        browser = _make_browser(
            active_session_fingerprint=None,
            active_session_started=None,
        )
        db.add(browser)
        db.commit()

        clear_active_session(browser, db)

        db.refresh(browser)
        assert browser.active_session_fingerprint is None
        assert browser.active_session_started is None
