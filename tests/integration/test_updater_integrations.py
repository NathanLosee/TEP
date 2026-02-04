"""Integration tests for updater routes."""

from unittest.mock import MagicMock, patch

from fastapi import status
from fastapi.testclient import TestClient

from src.main import app
from src.updater.constants import BASE_URL
from src.updater.routes import _get_settings
from src.updater.service import reset_state


def _github_release_response(tag="v1.1.0"):
    return {
        "tag_name": tag,
        "published_at": "2026-01-15T00:00:00Z",
        "body": "Bug fixes and improvements",
        "assets": [
            {
                "name": f"TAP-{tag.lstrip('v')}.zip",
                "browser_download_url": (
                    f"https://github.com/dl/"
                    f"TAP-{tag.lstrip('v')}.zip"
                ),
                "size": 50000000,
            }
        ],
    }


def _mock_settings(repo="owner/TAP", token=""):
    settings = MagicMock()
    settings.GITHUB_REPO = repo
    settings.GITHUB_TOKEN = token
    return settings


def test_get_status_200(test_client: TestClient):
    reset_state()
    response = test_client.get(f"{BASE_URL}/status")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["state"] == "idle"
    assert data["current_version"] == "1.0.0"
    assert data["update_available"] is False


@patch("src.updater.service.httpx.get")
def test_check_update_available(
    mock_get, test_client: TestClient
):
    reset_state()
    mock_response = MagicMock()
    mock_response.json.return_value = (
        _github_release_response()
    )
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    app.dependency_overrides[_get_settings] = lambda: (
        _mock_settings()
    )
    try:
        response = test_client.get(f"{BASE_URL}/check")
    finally:
        app.dependency_overrides.pop(_get_settings, None)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["version"] == "1.1.0"
    assert data["tag_name"] == "v1.1.0"
    assert "TAP-1.1.0.zip" in data["asset_name"]


@patch("src.updater.service.httpx.get")
def test_check_no_update(
    mock_get, test_client: TestClient
):
    reset_state()
    mock_response = MagicMock()
    mock_response.json.return_value = (
        _github_release_response(tag="v1.0.0")
    )
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    app.dependency_overrides[_get_settings] = lambda: (
        _mock_settings()
    )
    try:
        response = test_client.get(f"{BASE_URL}/check")
    finally:
        app.dependency_overrides.pop(_get_settings, None)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_check_repo_not_configured(
    test_client: TestClient,
):
    reset_state()

    app.dependency_overrides[_get_settings] = lambda: (
        _mock_settings(repo="")
    )
    try:
        response = test_client.get(f"{BASE_URL}/check")
    finally:
        app.dependency_overrides.pop(_get_settings, None)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_apply_not_frozen(test_client: TestClient):
    reset_state()
    response = test_client.post(f"{BASE_URL}/apply")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_rollback_not_frozen(test_client: TestClient):
    reset_state()
    response = test_client.post(f"{BASE_URL}/rollback")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@patch("src.updater.service.httpx.get")
def test_status_after_check(
    mock_get, test_client: TestClient
):
    reset_state()
    mock_response = MagicMock()
    mock_response.json.return_value = (
        _github_release_response()
    )
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    app.dependency_overrides[_get_settings] = lambda: (
        _mock_settings()
    )
    try:
        test_client.get(f"{BASE_URL}/check")
    finally:
        app.dependency_overrides.pop(_get_settings, None)

    response = test_client.get(f"{BASE_URL}/status")
    data = response.json()

    assert data["update_available"] is True
    assert data["latest_version"] == "1.1.0"
    assert data["last_checked"] is not None


def test_unauthorized_access(test_client: TestClient):
    reset_state()
    saved_headers = dict(test_client.headers)
    test_client.headers.clear()

    response = test_client.get(f"{BASE_URL}/status")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    test_client.headers.update(saved_headers)
