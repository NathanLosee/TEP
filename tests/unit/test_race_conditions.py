"""Unit tests for race condition handling in browser registration and license activation."""

from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from src.registered_browser.constants import (
    EXC_MSG_BROWSER_ALREADY_REGISTERED,
    EXC_MSG_BROWSER_NAME_ALREADY_EXISTS,
)


class TestBrowserRegistrationRaceConditions:
    """Tests for IntegrityError handling in browser registration.

    The register_browser route uses database constraints to prevent
    duplicate browser_uuid and browser_name, catching IntegrityError
    instead of using check-then-act patterns.
    """

    def _make_request(self, uuid="TEST-RACE-UUID-01", name="Race Browser"):
        """Create a mock RegisteredBrowserCreate."""
        req = Mock()
        req.browser_uuid = uuid
        req.browser_name = name
        req.fingerprint_hash = "test_fp"
        req.user_agent = "Test Agent"
        req.ip_address = None
        return req

    def _make_http_request(self):
        """Create a mock FastAPI Request."""
        req = Mock()
        req.client = Mock()
        req.client.host = "127.0.0.1"
        return req

    @patch("src.registered_browser.routes.create_event_log")
    @patch("src.registered_browser.routes.get_registered_browser_by_name")
    @patch("src.registered_browser.routes.get_registered_browser_by_uuid")
    @patch("src.registered_browser.routes.create_registered_browser_in_db")
    @patch("src.registered_browser.routes.validate_uuid_format", return_value=True)
    def test_integrity_error_duplicate_uuid_returns_409(
        self, mock_validate_fmt, mock_create, mock_get_uuid, mock_get_name,
        mock_event_log
    ):
        """IntegrityError on duplicate UUID should return 409 with browser_uuid field."""
        from src.registered_browser.routes import register_browser

        mock_create.side_effect = IntegrityError(None, None, Exception("UNIQUE"))
        mock_get_uuid.return_value = Mock()  # UUID exists
        mock_get_name.return_value = None

        db = MagicMock()
        request = self._make_request()

        with pytest.raises(HTTPException) as exc_info:
            register_browser(request, self._make_http_request(), db, "0", None)

        assert exc_info.value.status_code == 409
        assert exc_info.value.detail["field"] == "browser_uuid"
        assert exc_info.value.detail["message"] == EXC_MSG_BROWSER_ALREADY_REGISTERED

    @patch("src.registered_browser.routes.create_event_log")
    @patch("src.registered_browser.routes.get_registered_browser_by_name")
    @patch("src.registered_browser.routes.get_registered_browser_by_uuid")
    @patch("src.registered_browser.routes.create_registered_browser_in_db")
    @patch("src.registered_browser.routes.validate_uuid_format", return_value=True)
    def test_integrity_error_duplicate_name_returns_409(
        self, mock_validate_fmt, mock_create, mock_get_uuid, mock_get_name,
        mock_event_log
    ):
        """IntegrityError on duplicate name should return 409 with browser_name field."""
        from src.registered_browser.routes import register_browser

        mock_create.side_effect = IntegrityError(None, None, Exception("UNIQUE"))
        mock_get_uuid.return_value = None
        mock_get_name.return_value = Mock()  # Name exists

        db = MagicMock()
        request = self._make_request()

        with pytest.raises(HTTPException) as exc_info:
            register_browser(request, self._make_http_request(), db, "0", None)

        assert exc_info.value.status_code == 409
        assert exc_info.value.detail["field"] == "browser_name"
        assert exc_info.value.detail["message"] == EXC_MSG_BROWSER_NAME_ALREADY_EXISTS

    @patch("src.registered_browser.routes.create_event_log")
    @patch("src.registered_browser.routes.get_registered_browser_by_name")
    @patch("src.registered_browser.routes.get_registered_browser_by_uuid")
    @patch("src.registered_browser.routes.create_registered_browser_in_db")
    @patch("src.registered_browser.routes.validate_uuid_format", return_value=True)
    def test_integrity_error_generic_conflict(
        self, mock_validate_fmt, mock_create, mock_get_uuid, mock_get_name,
        mock_event_log
    ):
        """IntegrityError with neither constraint found should return generic 409."""
        from src.registered_browser.routes import register_browser

        mock_create.side_effect = IntegrityError(None, None, Exception("UNIQUE"))
        mock_get_uuid.return_value = None
        mock_get_name.return_value = None

        db = MagicMock()
        request = self._make_request()

        with pytest.raises(HTTPException) as exc_info:
            register_browser(request, self._make_http_request(), db, "0", None)

        assert exc_info.value.status_code == 409
        assert exc_info.value.detail["message"] == "Browser registration conflict"

    @patch("src.registered_browser.routes.create_event_log")
    @patch("src.registered_browser.routes.get_registered_browser_by_name")
    @patch("src.registered_browser.routes.get_registered_browser_by_uuid")
    @patch("src.registered_browser.routes.create_registered_browser_in_db")
    @patch("src.registered_browser.routes.validate_uuid_format", return_value=True)
    def test_rollback_called_on_integrity_error(
        self, mock_validate_fmt, mock_create, mock_get_uuid, mock_get_name,
        mock_event_log
    ):
        """Database session should be rolled back when IntegrityError occurs."""
        from src.registered_browser.routes import register_browser

        mock_create.side_effect = IntegrityError(None, None, Exception("UNIQUE"))
        mock_get_uuid.return_value = Mock()

        db = MagicMock()
        request = self._make_request()

        with pytest.raises(HTTPException):
            register_browser(request, self._make_http_request(), db, "0", None)

        db.rollback.assert_called_once()

    @patch("src.registered_browser.routes.create_event_log")
    @patch("src.registered_browser.routes.get_registered_browser_by_name")
    @patch("src.registered_browser.routes.get_registered_browser_by_uuid")
    @patch("src.registered_browser.routes.create_registered_browser_in_db")
    @patch("src.registered_browser.routes.validate_uuid_format", return_value=True)
    def test_successful_creation_no_integrity_handling(
        self, mock_validate_fmt, mock_create, mock_get_uuid, mock_get_name,
        mock_event_log
    ):
        """Successful creation should not trigger any IntegrityError handling."""
        from src.registered_browser.routes import register_browser

        mock_browser = Mock()
        mock_browser.id = 1
        mock_browser.browser_uuid = "TEST-RACE-UUID-01"
        mock_browser.browser_name = "Race Browser"
        mock_create.return_value = mock_browser

        db = MagicMock()
        request = self._make_request()

        result = register_browser(request, self._make_http_request(), db, "0", None)

        assert result == mock_browser
        mock_get_uuid.assert_not_called()
        mock_get_name.assert_not_called()
        db.rollback.assert_not_called()


class TestLicenseActivationRaceConditions:
    """Tests for race condition handling in license activation.

    The activate_license route has a check-then-act pattern and
    a non-atomic deactivate-then-activate sequence.
    """

    @patch("src.license.routes.create_event_log")
    @patch("src.license.routes.validate_license_key_format", return_value=True)
    @patch("src.license.routes.normalize_license_key", return_value="ab" * 64)
    @patch("src.license.routes.get_license_by_key")
    def test_active_license_returned_without_server_call(
        self, mock_get_by_key, mock_normalize, mock_validate_fmt, mock_event_log
    ):
        """If license is already active locally, skip license server call."""
        from src.license.routes import activate_license

        mock_license = Mock()
        mock_license.is_active = True
        mock_get_by_key.return_value = mock_license

        request = Mock()
        request.license_key = "ab" * 64
        db = MagicMock()

        with patch("src.license.routes.httpx") as mock_httpx:
            result = activate_license(request, db, "0")

        assert result == mock_license
        mock_httpx.Client.assert_not_called()

    @patch("src.license.routes.create_event_log")
    @patch("src.license.routes.set_license_activated")
    @patch("src.license.routes.create_license_in_db")
    @patch("src.license.routes.deactivate_all_licenses")
    @patch("src.license.routes.get_active_license", return_value=None)
    @patch("src.license.routes.get_machine_id", return_value="test-machine")
    @patch("src.license.routes.get_license_by_key", return_value=None)
    @patch("src.license.routes.normalize_license_key", return_value="ab" * 64)
    @patch("src.license.routes.validate_license_key_format", return_value=True)
    def test_deactivate_called_before_create(
        self, mock_validate_fmt, mock_normalize, mock_get_by_key,
        mock_machine_id, mock_get_active, mock_deactivate, mock_create,
        mock_set_activated, mock_event_log
    ):
        """deactivate_all_licenses must be called before create_license_in_db."""
        from src.license.routes import activate_license

        mock_new_license = Mock()
        mock_new_license.license_key = "ab" * 64
        mock_create.return_value = mock_new_license

        # Mock the httpx response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"activation_key": "key123"}

        request = Mock()
        request.license_key = "ab" * 64
        db = MagicMock()

        call_order = []
        mock_deactivate.side_effect = lambda *a, **k: call_order.append("deactivate")
        mock_create.side_effect = lambda *a, **k: (call_order.append("create"), mock_new_license)[1]

        with patch("src.license.routes.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=False)
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value = mock_client

            activate_license(request, db, "0")

        assert call_order == ["deactivate", "create"]

    @patch("src.license.routes.create_event_log")
    @patch("src.license.routes.set_license_activated")
    @patch("src.license.routes.reactivate_license_in_db")
    @patch("src.license.routes.deactivate_all_licenses")
    @patch("src.license.routes.get_active_license", return_value=None)
    @patch("src.license.routes.get_machine_id", return_value="test-machine")
    @patch("src.license.routes.normalize_license_key", return_value="ab" * 64)
    @patch("src.license.routes.validate_license_key_format", return_value=True)
    def test_deactivate_called_before_reactivate(
        self, mock_validate_fmt, mock_normalize, mock_machine_id,
        mock_get_active, mock_deactivate, mock_reactivate,
        mock_set_activated, mock_event_log
    ):
        """deactivate_all_licenses must be called before reactivate_license_in_db."""
        from src.license.routes import activate_license

        # Existing inactive license triggers reactivation path
        existing = Mock()
        existing.is_active = False
        existing.license_key = "ab" * 64

        mock_reactivated = Mock()
        mock_reactivated.license_key = "ab" * 64

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"activation_key": "key123"}

        request = Mock()
        request.license_key = "ab" * 64
        db = MagicMock()

        call_order = []
        mock_deactivate.side_effect = lambda *a, **k: call_order.append("deactivate")
        mock_reactivate.side_effect = lambda *a, **k: (call_order.append("reactivate"), mock_reactivated)[1]

        with patch("src.license.routes.get_license_by_key", return_value=existing):
            with patch("src.license.routes.httpx.Client") as mock_client_cls:
                mock_client = MagicMock()
                mock_client.__enter__ = Mock(return_value=mock_client)
                mock_client.__exit__ = Mock(return_value=False)
                mock_client.post.return_value = mock_response
                mock_client_cls.return_value = mock_client

                activate_license(request, db, "0")

        assert call_order == ["deactivate", "reactivate"]

    @patch("src.license.routes.create_event_log")
    @patch("src.license.routes.set_license_activated")
    @patch("src.license.routes.create_license_in_db")
    @patch("src.license.routes.deactivate_all_licenses")
    @patch("src.license.routes.get_active_license", return_value=None)
    @patch("src.license.routes.get_machine_id", return_value="test-machine")
    @patch("src.license.routes.get_license_by_key", return_value=None)
    @patch("src.license.routes.normalize_license_key", return_value="ab" * 64)
    @patch("src.license.routes.validate_license_key_format", return_value=True)
    def test_set_license_activated_called_after_create(
        self, mock_validate_fmt, mock_normalize, mock_get_by_key,
        mock_machine_id, mock_get_active, mock_deactivate, mock_create,
        mock_set_activated, mock_event_log
    ):
        """set_license_activated(True) must be called after license is created."""
        from src.license.routes import activate_license

        mock_new_license = Mock()
        mock_new_license.license_key = "ab" * 64
        mock_create.return_value = mock_new_license

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"activation_key": "key123"}

        request = Mock()
        request.license_key = "ab" * 64
        db = MagicMock()

        with patch("src.license.routes.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=False)
            mock_client.post.return_value = mock_response
            mock_client_cls.return_value = mock_client

            activate_license(request, db, "0")

        mock_set_activated.assert_called_once_with(True)


class TestLicenseActivationIntegrityError:
    """Tests for IntegrityError handling in license activation."""

    @patch("src.license.routes.create_event_log")
    @patch("src.license.routes.set_license_activated")
    @patch("src.license.routes.create_license_in_db")
    @patch("src.license.routes.deactivate_all_licenses")
    @patch(
        "src.license.routes.get_active_license",
        return_value=None,
    )
    @patch(
        "src.license.routes.get_machine_id",
        return_value="test-machine",
    )
    @patch(
        "src.license.routes.normalize_license_key",
        return_value="ab" * 64,
    )
    @patch(
        "src.license.routes.validate_license_key_format",
        return_value=True,
    )
    def test_integrity_error_returns_existing_license(
        self, mock_validate_fmt, mock_normalize,
        mock_machine_id, mock_get_active,
        mock_deactivate, mock_create,
        mock_set_activated, mock_event_log
    ):
        """IntegrityError during create should return
        existing active license."""
        from src.license.routes import activate_license

        mock_create.side_effect = IntegrityError(
            None, None, Exception("UNIQUE")
        )

        # After rollback, the existing license is found
        existing = Mock()
        existing.is_active = True
        existing.license_key = "ab" * 64

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "activation_key": "key123",
        }

        request = Mock()
        request.license_key = "ab" * 64
        db = MagicMock()

        with patch(
            "src.license.routes.get_license_by_key"
        ) as mock_get_by_key:
            mock_get_by_key.side_effect = [
                None, existing,
            ]
            with patch(
                "src.license.routes.httpx.Client"
            ) as mock_client_cls:
                mock_client = MagicMock()
                mock_client.__enter__ = Mock(
                    return_value=mock_client
                )
                mock_client.__exit__ = Mock(
                    return_value=False
                )
                mock_client.post.return_value = (
                    mock_response
                )
                mock_client_cls.return_value = mock_client

                result = activate_license(
                    request, db, "0"
                )

        assert result == existing
        db.rollback.assert_called_once()
        mock_set_activated.assert_called_once_with(True)

    @patch("src.license.routes.create_event_log")
    @patch("src.license.routes.set_license_activated")
    @patch("src.license.routes.create_license_in_db")
    @patch("src.license.routes.deactivate_all_licenses")
    @patch(
        "src.license.routes.get_active_license",
        return_value=None,
    )
    @patch(
        "src.license.routes.get_machine_id",
        return_value="test-machine",
    )
    @patch(
        "src.license.routes.normalize_license_key",
        return_value="ab" * 64,
    )
    @patch(
        "src.license.routes.validate_license_key_format",
        return_value=True,
    )
    def test_integrity_error_no_existing_raises_409(
        self, mock_validate_fmt, mock_normalize,
        mock_machine_id, mock_get_active,
        mock_deactivate, mock_create,
        mock_set_activated, mock_event_log
    ):
        """IntegrityError with no existing active license
        should raise 409."""
        from src.license.routes import activate_license

        mock_create.side_effect = IntegrityError(
            None, None, Exception("UNIQUE")
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "activation_key": "key123",
        }

        request = Mock()
        request.license_key = "ab" * 64
        db = MagicMock()

        with patch(
            "src.license.routes.get_license_by_key",
            return_value=None,
        ):
            with patch(
                "src.license.routes.httpx.Client"
            ) as mock_client_cls:
                mock_client = MagicMock()
                mock_client.__enter__ = Mock(
                    return_value=mock_client
                )
                mock_client.__exit__ = Mock(
                    return_value=False
                )
                mock_client.post.return_value = (
                    mock_response
                )
                mock_client_cls.return_value = mock_client

                with pytest.raises(HTTPException) as exc:
                    activate_license(request, db, "0")

        assert exc.value.status_code == 409
        db.rollback.assert_called_once()


class TestLicenseModelConstraints:
    """Tests documenting database constraints on the License model."""

    def test_license_key_has_unique_constraint(self):
        """License.license_key column should have a unique constraint."""
        from src.license.models import License

        col = License.__table__.columns["license_key"]
        assert col.unique is True

    def test_single_active_partial_unique_index_exists(self):
        """License model should have a partial unique index enforcing
        at most one active license at a time."""
        from src.license.models import License

        index_names = [
            idx.name for idx in License.__table__.indexes
        ]
        assert "ix_licenses_single_active" in index_names
