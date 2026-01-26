"""Integration tests for system settings endpoints."""

import io

from fastapi import status
from fastapi.testclient import TestClient

from src.system_settings.constants import (
    BASE_URL,
    EXC_MSG_INVALID_LOGO_TYPE,
    EXC_MSG_LOGO_TOO_LARGE,
    MAX_LOGO_SIZE,
)


def test_get_system_settings_200(test_client: TestClient):
    """Test getting current system settings."""
    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert "primary_color" in data
    assert "secondary_color" in data
    assert "accent_color" in data
    assert "company_name" in data
    assert "has_logo" in data
    assert "logo_filename" in data


def test_get_system_settings_public_no_auth(test_client: TestClient):
    """Test that getting system settings does not require authentication."""
    # Clear authentication headers
    original_headers = test_client.headers.copy()
    test_client.headers.clear()

    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert "primary_color" in response.json()

    # Restore headers
    test_client.headers.update(original_headers)


def test_update_system_settings_200(test_client: TestClient):
    """Test successfully updating system settings."""
    update_data = {
        "company_name": "Test Company",
        "primary_color": "#123456",
        "secondary_color": "#654321",
        "accent_color": "#ABCDEF",
    }

    response = test_client.put(BASE_URL, json=update_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["company_name"] == "Test Company"
    assert data["primary_color"] == "#123456"
    assert data["secondary_color"] == "#654321"
    assert data["accent_color"] == "#ABCDEF"


def test_update_system_settings_partial(test_client: TestClient):
    """Test updating only some settings."""
    update_data = {
        "company_name": "Partial Update Corp",
    }

    response = test_client.put(BASE_URL, json=update_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["company_name"] == "Partial Update Corp"
    # Other fields should remain unchanged
    assert "primary_color" in data


def test_update_system_settings_requires_auth(test_client: TestClient):
    """Test that updating system settings requires authentication."""
    # Clear authentication headers
    original_headers = test_client.headers.copy()
    test_client.headers.clear()

    update_data = {"company_name": "Should Fail"}
    response = test_client.put(BASE_URL, json=update_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Restore headers
    test_client.headers.update(original_headers)


def test_upload_logo_200(test_client: TestClient):
    """Test successfully uploading a logo."""
    # Create a simple PNG file (1x1 pixel transparent PNG)
    png_data = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
        b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    files = {"file": ("logo.png", io.BytesIO(png_data), "image/png")}
    response = test_client.post(f"{BASE_URL}/logo", files=files)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["has_logo"] is True
    assert data["logo_filename"] == "logo.png"


def test_upload_logo_400_invalid_type(test_client: TestClient):
    """Test uploading a logo with invalid file type."""
    files = {"file": ("logo.txt", io.BytesIO(b"not an image"), "text/plain")}
    response = test_client.post(f"{BASE_URL}/logo", files=files)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == EXC_MSG_INVALID_LOGO_TYPE


def test_upload_logo_400_too_large(test_client: TestClient):
    """Test uploading a logo that exceeds size limit."""
    # Create data larger than MAX_LOGO_SIZE
    large_data = b"\x00" * (MAX_LOGO_SIZE + 1)

    files = {"file": ("logo.png", io.BytesIO(large_data), "image/png")}
    response = test_client.post(f"{BASE_URL}/logo", files=files)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == EXC_MSG_LOGO_TOO_LARGE


def test_upload_logo_requires_auth(test_client: TestClient):
    """Test that uploading a logo requires authentication."""
    # Clear authentication headers
    original_headers = test_client.headers.copy()
    test_client.headers.clear()

    png_data = b"\x89PNG\r\n\x1a\n"
    files = {"file": ("logo.png", io.BytesIO(png_data), "image/png")}
    response = test_client.post(f"{BASE_URL}/logo", files=files)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Restore headers
    test_client.headers.update(original_headers)


def test_get_logo_200(test_client: TestClient):
    """Test getting the logo after upload."""
    # First upload a logo
    png_data = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
        b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    files = {"file": ("logo.png", io.BytesIO(png_data), "image/png")}
    test_client.post(f"{BASE_URL}/logo", files=files)

    # Then retrieve it
    response = test_client.get(f"{BASE_URL}/logo")

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == "image/png"
    assert len(response.content) > 0


def test_get_logo_204_no_logo(test_client: TestClient):
    """Test getting logo when none exists."""
    # Delete any existing logo
    test_client.delete(f"{BASE_URL}/logo")

    response = test_client.get(f"{BASE_URL}/logo")

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_get_logo_public_no_auth(test_client: TestClient):
    """Test that getting the logo does not require authentication."""
    # Clear authentication headers
    original_headers = test_client.headers.copy()
    test_client.headers.clear()

    response = test_client.get(f"{BASE_URL}/logo")

    # Should work without auth (either 200 or 204 depending on logo existence)
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]

    # Restore headers
    test_client.headers.update(original_headers)


def test_delete_logo_204(test_client: TestClient):
    """Test successfully deleting the logo."""
    # First upload a logo
    png_data = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
        b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    files = {"file": ("logo.png", io.BytesIO(png_data), "image/png")}
    test_client.post(f"{BASE_URL}/logo", files=files)

    # Delete logo
    response = test_client.delete(f"{BASE_URL}/logo")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify logo is deleted
    settings_response = test_client.get(BASE_URL)
    assert settings_response.json()["has_logo"] is False


def test_delete_logo_requires_auth(test_client: TestClient):
    """Test that deleting the logo requires authentication."""
    # Clear authentication headers
    original_headers = test_client.headers.copy()
    test_client.headers.clear()

    response = test_client.delete(f"{BASE_URL}/logo")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Restore headers
    test_client.headers.update(original_headers)


def test_update_settings_invalid_color_format(test_client: TestClient):
    """Test updating with invalid color format."""
    update_data = {
        "primary_color": "invalid-color",
    }

    response = test_client.put(BASE_URL, json=update_data)

    # Pydantic validation should reject invalid hex colors
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_settings_persistence(test_client: TestClient):
    """Test that settings changes persist."""
    # Update settings
    update_data = {
        "company_name": "Persistence Test Corp",
        "primary_color": "#AABBCC",
    }
    test_client.put(BASE_URL, json=update_data)

    # Get settings again
    response = test_client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["company_name"] == "Persistence Test Corp"
    assert data["primary_color"] == "#AABBCC"
