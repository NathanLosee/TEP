"""Integration tests for license management endpoints."""

from unittest.mock import MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient

from src.license.constants import (
    BASE_URL,
    EXC_MSG_INVALID_LICENSE_KEY,
    EXC_MSG_LICENSE_NOT_FOUND,
)
from tests.conftest import generate_test_license_key


def mock_license_server_response(activation_key: str = "b" * 128):
    """Create a mock httpx response for the license server."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"activation_key": activation_key}
    return mock_response


def mock_license_server_error(error_detail: str = "Invalid license key"):
    """Create a mock httpx error response for the license server."""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"detail": error_detail}
    return mock_response


def test_get_license_status_200_no_license(test_client: TestClient):
    # Deactivate the auto-activated license first
    test_client.delete(f"{BASE_URL}/deactivate")

    """Test getting license status when no license is active."""
    response = test_client.get(f"{BASE_URL}/status")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_active"] is False
    assert response.json()["license_key"] is None
    assert response.json()["activated_at"] is None


@patch("src.license.routes.httpx.Client")
def test_activate_license_201(mock_client, test_client: TestClient):
    """Test successfully activating a license."""
    # Mock the license server response
    mock_client.return_value.__enter__.return_value.post.return_value = (
        mock_license_server_response()
    )

    license_key = generate_test_license_key()

    response = test_client.post(
        f"{BASE_URL}/activate",
        json={"license_key": license_key},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["license_key"] == license_key
    assert response.json()["is_active"] is True
    assert "activated_at" in response.json()
    assert "id" in response.json()


def test_activate_license_400_invalid_format(test_client: TestClient):
    """Test activating with invalid license key format."""
    invalid_license_key = "INVALID-FORMAT"

    response = test_client.post(
        f"{BASE_URL}/activate",
        json={"license_key": invalid_license_key},
    )

    # Pydantic validation returns 400 with validation error as string
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    # Response is a string containing the validation error details
    response_data = response.json()
    assert isinstance(response_data, str)
    assert "license_key" in response_data or "validation" in response_data.lower()


@patch("src.license.routes.httpx.Client")
def test_activate_license_400_invalid_signature(
    mock_client, test_client: TestClient
):
    """Test activating with invalid signature (license key)."""
    # Mock the license server rejecting the key
    mock_client.return_value.__enter__.return_value.post.return_value = (
        mock_license_server_error("Invalid license key")
    )

    invalid_license_key = "a" * 128  # Valid format but invalid signature

    response = test_client.post(
        f"{BASE_URL}/activate",
        json={"license_key": invalid_license_key},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@patch("src.license.routes.httpx.Client")
def test_activate_same_license_returns_existing(
    mock_client, test_client: TestClient
):
    """Test activating the same license key twice returns the existing license."""
    # Mock the license server response
    mock_client.return_value.__enter__.return_value.post.return_value = (
        mock_license_server_response()
    )

    license_key = generate_test_license_key()

    # Activate first time
    response1 = test_client.post(
        f"{BASE_URL}/activate",
        json={"license_key": license_key},
    )
    assert response1.status_code == status.HTTP_201_CREATED

    # Try to activate again - should return the existing license (not error)
    response2 = test_client.post(
        f"{BASE_URL}/activate",
        json={"license_key": license_key},
    )

    # Current implementation returns the existing active license
    assert response2.status_code == status.HTTP_201_CREATED
    assert response2.json()["license_key"] == license_key
    assert response2.json()["is_active"] is True


@patch("src.license.routes.httpx.Client")
def test_get_license_status_200_with_active_license(
    mock_client, test_client: TestClient
):
    """Test getting license status when a license is active."""
    # Mock the license server response
    mock_client.return_value.__enter__.return_value.post.return_value = (
        mock_license_server_response()
    )

    license_key = generate_test_license_key()

    # Activate license
    test_client.post(
        f"{BASE_URL}/activate",
        json={"license_key": license_key},
    )

    # Check status
    response = test_client.get(f"{BASE_URL}/status")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_active"] is True
    assert response.json()["license_key"] == license_key
    assert response.json()["activated_at"] is not None


@patch("src.license.routes.httpx.Client")
def test_deactivate_license_204(mock_client, test_client: TestClient):
    """Test successfully deactivating a license."""
    # Mock the license server response
    mock_client.return_value.__enter__.return_value.post.return_value = (
        mock_license_server_response()
    )

    license_key = generate_test_license_key()

    # Activate license
    test_client.post(
        f"{BASE_URL}/activate",
        json={"license_key": license_key},
    )

    # Deactivate license
    response = test_client.delete(f"{BASE_URL}/deactivate")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify license is deactivated
    status_response = test_client.get(f"{BASE_URL}/status")
    assert status_response.json()["is_active"] is False


def test_deactivate_license_404_no_active_license(test_client: TestClient):
    """Test deactivating when no license is active."""
    # Deactivate the auto-activated license first
    test_client.delete(f"{BASE_URL}/deactivate")

    response = test_client.delete(f"{BASE_URL}/deactivate")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == EXC_MSG_LICENSE_NOT_FOUND


@patch("src.license.routes.httpx.Client")
def test_activate_replaces_previous_license(
    mock_client, test_client: TestClient
):
    """Test that activating a new license deactivates the previous one."""
    # Mock the license server response
    mock_client.return_value.__enter__.return_value.post.return_value = (
        mock_license_server_response()
    )

    # Activate first license
    license_key1 = generate_test_license_key()
    test_client.post(
        f"{BASE_URL}/activate",
        json={"license_key": license_key1},
    )

    # Activate second license
    license_key2 = generate_test_license_key()
    response = test_client.post(
        f"{BASE_URL}/activate",
        json={"license_key": license_key2},
    )

    assert response.status_code == status.HTTP_201_CREATED

    # Verify only second license is active
    status_response = test_client.get(f"{BASE_URL}/status")
    assert status_response.json()["is_active"] is True
    assert status_response.json()["license_key"] == license_key2


def test_license_status_public_no_auth_required(test_client: TestClient):
    """Test that license status endpoint does not require authentication."""
    # Clear authentication headers
    original_headers = test_client.headers.copy()
    test_client.headers.clear()

    # Should still work without auth
    response = test_client.get(f"{BASE_URL}/status")

    assert response.status_code == status.HTTP_200_OK
    assert "is_active" in response.json()

    # Restore headers
    test_client.headers.update(original_headers)


@patch("src.license.routes.httpx.Client")
def test_activate_license_requires_auth(mock_client, test_client: TestClient):
    """Test that activating a license requires authentication."""
    license_key = generate_test_license_key()

    # Clear authentication headers
    original_headers = test_client.headers.copy()
    test_client.headers.clear()

    response = test_client.post(
        f"{BASE_URL}/activate",
        json={"license_key": license_key},
    )

    # Should fail without auth
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Restore headers
    test_client.headers.update(original_headers)


def test_deactivate_license_requires_auth(test_client: TestClient):
    """Test that deactivating a license requires authentication."""
    # Clear authentication headers
    original_headers = test_client.headers.copy()
    test_client.headers.clear()

    response = test_client.delete(f"{BASE_URL}/deactivate")

    # Should fail without auth
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Restore headers
    test_client.headers.update(original_headers)
