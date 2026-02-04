"""Unit tests for updater service."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from src.updater.service import (
    check_for_update,
    compare_versions,
    get_status,
    reset_state,
)


@pytest.fixture(autouse=True)
def clean_state():
    """Reset updater state before each test."""
    reset_state()
    yield
    reset_state()


class TestCompareVersions:
    def test_equal(self):
        assert compare_versions("1.0.0", "1.0.0") == 0

    def test_current_older(self):
        assert compare_versions("1.0.0", "1.1.0") == -1

    def test_current_newer(self):
        assert compare_versions("2.0.0", "1.9.9") == 1

    def test_patch_older(self):
        assert compare_versions("1.0.0", "1.0.1") == -1

    def test_major_older(self):
        assert compare_versions("1.9.9", "2.0.0") == -1

    def test_v_prefix(self):
        assert compare_versions("v1.0.0", "v1.0.0") == 0
        assert compare_versions("v1.0.0", "v1.1.0") == -1

    def test_short_version(self):
        assert compare_versions("1.0", "1.0.0") == 0
        assert compare_versions("1", "1.0.0") == 0

    def test_mixed_prefix(self):
        assert compare_versions("1.0.0", "v1.0.0") == 0


class TestCheckForUpdate:
    def _mock_settings(self, repo="owner/TAP", token=""):
        settings = MagicMock()
        settings.GITHUB_REPO = repo
        settings.GITHUB_TOKEN = token
        return settings

    def _github_response(
        self, tag="v1.1.0", asset_name="TAP-1.1.0.zip"
    ):
        return {
            "tag_name": tag,
            "published_at": "2026-01-15T00:00:00Z",
            "body": "Bug fixes and improvements",
            "assets": [
                {
                    "name": asset_name,
                    "browser_download_url": (
                        f"https://github.com/dl/{asset_name}"
                    ),
                    "size": 50000000,
                }
            ],
        }

    def test_repo_not_configured(self):
        settings = self._mock_settings(repo="")
        with pytest.raises(ValueError, match="not configured"):
            check_for_update(settings)

    @patch("src.updater.service.get_current_version")
    @patch("src.updater.service.httpx.get")
    def test_new_version_available(self, mock_get, mock_ver):
        mock_ver.return_value = "1.0.0"
        mock_response = MagicMock()
        mock_response.json.return_value = self._github_response()
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = check_for_update(self._mock_settings())

        assert result is not None
        assert result.version == "1.1.0"
        assert result.asset_name == "TAP-1.1.0.zip"
        assert "github.com" in result.download_url

    @patch("src.updater.service.get_current_version")
    @patch("src.updater.service.httpx.get")
    def test_up_to_date(self, mock_get, mock_ver):
        mock_ver.return_value = "1.1.0"
        mock_response = MagicMock()
        mock_response.json.return_value = self._github_response(
            tag="v1.1.0"
        )
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = check_for_update(self._mock_settings())

        assert result is None

    @patch("src.updater.service.get_current_version")
    @patch("src.updater.service.httpx.get")
    def test_current_newer(self, mock_get, mock_ver):
        mock_ver.return_value = "2.0.0"
        mock_response = MagicMock()
        mock_response.json.return_value = self._github_response(
            tag="v1.1.0"
        )
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = check_for_update(self._mock_settings())

        assert result is None

    @patch("src.updater.service.get_current_version")
    @patch("src.updater.service.httpx.get")
    def test_no_zip_asset(self, mock_get, mock_ver):
        mock_ver.return_value = "1.0.0"
        data = self._github_response()
        data["assets"] = [
            {"name": "source.tar.gz", "size": 1000}
        ]
        mock_response = MagicMock()
        mock_response.json.return_value = data
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = check_for_update(self._mock_settings())

        assert result is None

    @patch("src.updater.service.get_current_version")
    @patch("src.updater.service.httpx.get")
    def test_github_api_error(self, mock_get, mock_ver):
        mock_ver.return_value = "1.0.0"
        mock_get.side_effect = httpx.HTTPStatusError(
            "Not found",
            request=MagicMock(),
            response=MagicMock(status_code=404),
        )

        with pytest.raises(httpx.HTTPStatusError):
            check_for_update(self._mock_settings())

        status = get_status()
        assert status.state == "error"

    @patch("src.updater.service.get_current_version")
    @patch("src.updater.service.httpx.get")
    def test_with_auth_token(self, mock_get, mock_ver):
        mock_ver.return_value = "1.0.0"
        mock_response = MagicMock()
        mock_response.json.return_value = self._github_response()
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        check_for_update(
            self._mock_settings(token="ghp_test123")
        )

        call_kwargs = mock_get.call_args
        headers = call_kwargs.kwargs.get(
            "headers", call_kwargs[1].get("headers", {})
        )
        assert "Bearer ghp_test123" in headers.get(
            "Authorization", ""
        )


class TestGetStatus:
    @patch("src.updater.service.get_current_version")
    def test_initial_state(self, mock_ver):
        mock_ver.return_value = "1.0.0"
        status = get_status()

        assert status.current_version == "1.0.0"
        assert status.state == "idle"
        assert status.update_available is False
        assert status.latest_version is None
        assert status.download_progress is None
        assert status.error is None

    @patch("src.updater.service.get_current_version")
    @patch("src.updater.service.httpx.get")
    def test_state_after_check(self, mock_get, mock_ver):
        mock_ver.return_value = "1.0.0"
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "tag_name": "v1.1.0",
            "published_at": "2026-01-15T00:00:00Z",
            "body": "Changes",
            "assets": [
                {
                    "name": "TAP-1.1.0.zip",
                    "browser_download_url": "https://dl/TAP.zip",
                    "size": 50000000,
                }
            ],
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        settings = MagicMock()
        settings.GITHUB_REPO = "owner/TAP"
        settings.GITHUB_TOKEN = ""

        check_for_update(settings)

        status = get_status()
        assert status.update_available is True
        assert status.latest_version == "1.1.0"
        assert status.last_checked is not None
        assert status.state == "idle"
