"""Integration tests for race condition handling under concurrent requests."""

import concurrent.futures
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy import select

from src.license.constants import BASE_URL as LICENSE_URL
from src.license.models import License
from src.registered_browser.constants import BASE_URL as BROWSER_URL
from src.registered_browser.models import RegisteredBrowser
from tests.conftest import TestingSessionLocal, generate_test_license_key


def _count_browsers_with_uuid(uuid: str) -> int:
    """Count browsers with a given UUID in the test database."""
    db = TestingSessionLocal()
    try:
        return len(
            db.scalars(
                select(RegisteredBrowser).where(
                    RegisteredBrowser.browser_uuid == uuid
                )
            ).all()
        )
    finally:
        db.close()


def _count_browsers_with_name(name: str) -> int:
    """Count browsers with a given name in the test database."""
    db = TestingSessionLocal()
    try:
        return len(
            db.scalars(
                select(RegisteredBrowser).where(
                    RegisteredBrowser.browser_name == name
                )
            ).all()
        )
    finally:
        db.close()


def _count_active_licenses() -> int:
    """Count active licenses in the test database."""
    db = TestingSessionLocal()
    try:
        return len(
            db.scalars(
                select(License).where(
                    License.is_active == True  # noqa: E712
                )
            ).all()
        )
    finally:
        db.close()


def test_concurrent_register_same_uuid_one_succeeds(
    test_client: TestClient,
):
    """Two concurrent registrations with the same UUID:
    one succeeds, one gets 409."""
    uuid = "RACE-STORM-PEAK-11"

    def register(name):
        return test_client.post(
            BROWSER_URL,
            json={
                "browser_uuid": uuid,
                "browser_name": name,
                "fingerprint_hash": f"fp_{name}",
                "user_agent": "Test Agent",
            },
        )

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=2
    ) as executor:
        future1 = executor.submit(register, "Race Alpha")
        future2 = executor.submit(register, "Race Beta")
        results = [future1.result(), future2.result()]

    status_codes = sorted([r.status_code for r in results])
    assert status_codes == [201, 409], (
        f"Expected [201, 409], got {status_codes}"
    )

    # Post-condition: exactly one browser with that UUID
    assert _count_browsers_with_uuid(uuid) == 1


def test_concurrent_register_same_name_one_succeeds(
    test_client: TestClient,
):
    """Two concurrent registrations with the same name:
    one succeeds, one gets 409."""
    name = "Race Concurrent Browser"

    def register(uuid):
        return test_client.post(
            BROWSER_URL,
            json={
                "browser_uuid": uuid,
                "browser_name": name,
                "fingerprint_hash": f"fp_{uuid}",
                "user_agent": "Test Agent",
            },
        )

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=2
    ) as executor:
        future1 = executor.submit(
            register, "RACE-WIND-FIRE-21"
        )
        future2 = executor.submit(
            register, "RACE-SNOW-MOON-22"
        )
        results = [future1.result(), future2.result()]

    status_codes = sorted([r.status_code for r in results])
    assert status_codes == [201, 409], (
        f"Expected [201, 409], got {status_codes}"
    )

    # Post-condition: exactly one browser with that name
    assert _count_browsers_with_name(name) == 1


@patch("src.license.routes.httpx.Client")
def test_concurrent_activate_same_license_key(
    mock_client, test_client: TestClient
):
    """Two concurrent activations with the same key:
    one creates, the other returns existing or gets 409."""
    mock_response = MagicMock(
        status_code=200,
        json=MagicMock(
            return_value={"activation_key": "c" * 128}
        ),
    )
    mock_client.return_value.__enter__.return_value.post\
        .return_value = mock_response

    license_key = generate_test_license_key()

    def activate():
        return test_client.post(
            f"{LICENSE_URL}/activate",
            json={"license_key": license_key},
        )

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=2
    ) as executor:
        future1 = executor.submit(activate)
        future2 = executor.submit(activate)
        results = [future1.result(), future2.result()]

    # At least one succeeds; the other succeeds or gets 409
    assert any(
        r.status_code in (200, 201) for r in results
    ), "Expected at least one success"
    for r in results:
        assert r.status_code in (200, 201, 409), (
            f"Unexpected status {r.status_code}"
        )

    # Post-condition: exactly one license record
    db = TestingSessionLocal()
    try:
        count = len(
            db.scalars(
                select(License).where(
                    License.license_key == license_key
                )
            ).all()
        )
        assert count == 1
    finally:
        db.close()


@patch("src.license.routes.httpx.Client")
def test_concurrent_activate_different_keys_one_active(
    mock_client, test_client: TestClient
):
    """Two concurrent activations with different keys:
    exactly one should be active after, enforced by the
    partial unique index on is_active."""
    mock_response = MagicMock(
        status_code=200,
        json=MagicMock(
            return_value={"activation_key": "d" * 128}
        ),
    )
    mock_client.return_value.__enter__.return_value.post\
        .return_value = mock_response

    key1 = generate_test_license_key()
    key2 = generate_test_license_key()

    def activate(key):
        return test_client.post(
            f"{LICENSE_URL}/activate",
            json={"license_key": key},
        )

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=2
    ) as executor:
        future1 = executor.submit(activate, key1)
        future2 = executor.submit(activate, key2)
        results = [future1.result(), future2.result()]

    # At least one succeeds; the other may get 409
    # from the partial unique index constraint
    assert any(
        r.status_code in (200, 201) for r in results
    ), "Expected at least one success"
    for r in results:
        assert r.status_code in (200, 201, 409), (
            f"Unexpected status {r.status_code}"
        )

    # Post-condition: exactly one active license
    active_count = _count_active_licenses()
    assert active_count == 1, (
        f"Expected exactly 1 active license, got "
        f"{active_count}"
    )
