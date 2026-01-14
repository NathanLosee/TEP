"""Integration tests for registered browser management endpoints."""

from fastapi import status
from fastapi.testclient import TestClient

from src.registered_browser.constants import (
    BASE_URL,
    EXC_MSG_BROWSER_ALREADY_REGISTERED,
    EXC_MSG_BROWSER_NAME_ALREADY_EXISTS,
    EXC_MSG_BROWSER_NOT_FOUND,
)


def test_register_browser_201_with_auto_generated_uuid(test_client: TestClient):
    """Test registering a browser with auto-generated UUID."""
    response = test_client.post(
        BASE_URL,
        json={
            "browser_name": "Auto UUID Test Browser",
            "fingerprint_hash": "auto_test_fingerprint_123",
            "user_agent": "Test Agent",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert "browser_uuid" in response.json()
    assert response.json()["browser_name"] == "Auto UUID Test Browser"
    # Verify UUID format: WORD-WORD-WORD-NUMBER
    uuid_parts = response.json()["browser_uuid"].split("-")
    assert len(uuid_parts) == 4
    assert uuid_parts[0].isupper() and uuid_parts[0].isalpha()
    assert uuid_parts[1].isupper() and uuid_parts[1].isalpha()
    assert uuid_parts[2].isupper() and uuid_parts[2].isalpha()
    assert uuid_parts[3].isdigit() and len(uuid_parts[3]) == 2


def test_register_browser_201_with_custom_uuid(test_client: TestClient):
    """Test registering a browser with custom UUID."""
    custom_uuid = "EAGLE-RIVER-MOUNTAIN-42"
    response = test_client.post(
        BASE_URL,
        json={
            "browser_uuid": custom_uuid,
            "browser_name": "Custom UUID Test Browser",
            "fingerprint_hash": "custom_test_fingerprint_456",
            "user_agent": "Test Agent",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["browser_uuid"] == custom_uuid
    assert response.json()["browser_name"] == "Custom UUID Test Browser"


def test_register_browser_400_invalid_uuid_format(test_client: TestClient):
    """Test registering with invalid UUID format."""
    invalid_uuid = "INVALID-FORMAT"
    response = test_client.post(
        BASE_URL,
        json={
            "browser_uuid": invalid_uuid,
            "browser_name": "Invalid UUID Browser",
            "fingerprint_hash": "test_fingerprint",
            "user_agent": "Test Agent",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid UUID format" in response.json()["detail"]


def test_register_browser_409_uuid_already_exists(test_client: TestClient):
    """Test registering the same UUID twice returns 409."""
    browser_uuid = "TIGER-CLOUD-JADE-88"
    test_client.post(
        BASE_URL,
        json={
            "browser_uuid": browser_uuid,
            "browser_name": "First Browser",
            "fingerprint_hash": "fingerprint_1",
            "user_agent": "Test Agent",
        },
    )

    # Try to register again with same UUID
    response = test_client.post(
        BASE_URL,
        json={
            "browser_uuid": browser_uuid,
            "browser_name": "Second Browser",
            "fingerprint_hash": "fingerprint_2",
            "user_agent": "Test Agent",
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_BROWSER_ALREADY_REGISTERED


def test_register_browser_409_name_already_exists(test_client: TestClient):
    """Test registering the same browser name twice returns 409."""
    browser_name = "Duplicate Name Browser"
    test_client.post(
        BASE_URL,
        json={
            "browser_name": browser_name,
            "fingerprint_hash": "fingerprint_a",
            "user_agent": "Test Agent",
        },
    )

    # Try to register again with same name
    response = test_client.post(
        BASE_URL,
        json={
            "browser_name": browser_name,
            "fingerprint_hash": "fingerprint_b",
            "user_agent": "Test Agent",
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == EXC_MSG_BROWSER_NAME_ALREADY_EXISTS


def test_verify_browser_by_uuid(test_client: TestClient):
    """Test verifying browser by UUID."""
    # Register a browser
    register_response = test_client.post(
        BASE_URL,
        json={
            "browser_uuid": "WOLF-PEAK-STORM-55",
            "browser_name": "Verify Test Browser",
            "fingerprint_hash": "verify_fingerprint",
            "user_agent": "Test Agent",
        },
    )
    browser_uuid = register_response.json()["browser_uuid"]

    # Verify browser
    response = test_client.post(
        f"{BASE_URL}/verify",
        json={
            "browser_uuid": browser_uuid,
            "fingerprint_hash": "verify_fingerprint",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["verified"] is True
    assert response.json()["browser_uuid"] == browser_uuid
    assert response.json()["browser_name"] == "Verify Test Browser"


def test_verify_browser_by_fingerprint(test_client: TestClient):
    """Test verifying browser by fingerprint when UUID not provided."""
    fingerprint = "unique_fingerprint_789"
    # Register a browser
    register_response = test_client.post(
        BASE_URL,
        json={
            "browser_name": "Fingerprint Test Browser",
            "fingerprint_hash": fingerprint,
            "user_agent": "Test Agent",
        },
    )
    browser_uuid = register_response.json()["browser_uuid"]

    # Verify browser using fingerprint only
    response = test_client.post(
        f"{BASE_URL}/verify",
        json={
            "fingerprint_hash": fingerprint,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["verified"] is True
    assert response.json()["browser_uuid"] == browser_uuid
    assert response.json()["restored"] is True  # UUID was restored from fingerprint


def test_verify_browser_not_found(test_client: TestClient):
    """Test verifying browser that doesn't exist."""
    response = test_client.post(
        f"{BASE_URL}/verify",
        json={
            "browser_uuid": "NONEXISTENT-UUID-TEST-99",
            "fingerprint_hash": "unknown_fingerprint",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["verified"] is False
    assert response.json()["browser_uuid"] is None


def test_recover_browser_200(test_client: TestClient):
    """Test successfully recovering browser with device ID."""
    # Register a browser
    register_response = test_client.post(
        BASE_URL,
        json={
            "browser_uuid": "OCEAN-MOUNTAIN-FIRE-33",
            "browser_name": "Recovery Test Browser",
            "fingerprint_hash": "original_fingerprint",
            "user_agent": "Test Agent",
        },
    )
    device_id = register_response.json()["browser_uuid"]

    # Recover browser with new fingerprint
    new_fingerprint = "new_fingerprint_after_clear"
    response = test_client.post(
        f"{BASE_URL}/recover",
        json={
            "recovery_code": device_id,
            "fingerprint_hash": new_fingerprint,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["browser_uuid"] == device_id
    assert response.json()["browser_name"] == "Recovery Test Browser"
    assert response.json()["recovered"] is True


def test_recover_browser_400_invalid_format(test_client: TestClient):
    """Test recovering with invalid device ID format."""
    response = test_client.post(
        f"{BASE_URL}/recover",
        json={
            "recovery_code": "INVALID",
            "fingerprint_hash": "some_fingerprint",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid device ID format" in response.json()["detail"]


def test_recover_browser_404_not_found(test_client: TestClient):
    """Test recovering with non-existent device ID."""
    response = test_client.post(
        f"{BASE_URL}/recover",
        json={
            "recovery_code": "FAKE-DEVICE-UUID-99",
            "fingerprint_hash": "some_fingerprint",
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Device ID not found" in response.json()["detail"]


def test_get_registered_browsers_200(test_client: TestClient):
    """Test retrieving all registered browsers."""
    # Register a browser first
    register_response = test_client.post(
        BASE_URL,
        json={
            "browser_name": "List Test Browser",
            "fingerprint_hash": "list_test_fingerprint",
            "user_agent": "Test Agent",
        },
    )
    browser_uuid = register_response.json()["browser_uuid"]

    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
    # Check that our registered browser is in the list
    uuids = [browser["browser_uuid"] for browser in response.json()]
    assert browser_uuid in uuids


def test_delete_registered_browser_204(test_client: TestClient):
    """Test successfully deleting a registered browser."""
    # Register a browser first
    register_response = test_client.post(
        BASE_URL,
        json={
            "browser_name": "Delete Test Browser",
            "fingerprint_hash": "delete_test_fingerprint",
            "user_agent": "Test Agent",
        },
    )
    browser_id = register_response.json()["id"]
    browser_uuid = register_response.json()["browser_uuid"]

    response = test_client.delete(f"{BASE_URL}/{browser_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify browser is deleted
    get_response = test_client.get(BASE_URL)
    uuids = [browser["browser_uuid"] for browser in get_response.json()]
    assert browser_uuid not in uuids


def test_delete_registered_browser_404_not_found(test_client: TestClient):
    """Test deleting a non-existent browser returns 404."""
    fake_id = 999999

    response = test_client.delete(f"{BASE_URL}/{fake_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_BROWSER_NOT_FOUND
