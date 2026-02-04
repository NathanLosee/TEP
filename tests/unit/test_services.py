"""Unit tests for core service functions."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi import HTTPException

from src.services import (
    create_event_log,
    get_scopes_from_user,
    hash_password,
    validate,
    verify_password,
)


class TestValidate:
    """Tests for the validate function."""

    def test_true_condition_returns_true(self):
        """A truthy condition should return True without raising."""
        result = validate(True, "should not raise")
        assert result is True

    def test_false_condition_raises_http_exception(self):
        """A falsy condition should raise HTTPException with the message."""
        with pytest.raises(HTTPException) as exc_info:
            validate(False, "validation failed", 400)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "validation failed"

    def test_false_condition_with_custom_status_code(self):
        """HTTPException should use the provided status code."""
        with pytest.raises(HTTPException) as exc_info:
            validate(False, "not found", 404)
        assert exc_info.value.status_code == 404

    def test_structured_error_with_field_and_constraint(self):
        """When field and constraint are provided, detail should be a dict."""
        with pytest.raises(HTTPException) as exc_info:
            validate(
                False, "Name taken", 409,
                field="name", constraint="unique"
            )
        detail = exc_info.value.detail
        assert isinstance(detail, dict)
        assert detail["message"] == "Name taken"
        assert detail["field"] == "name"
        assert detail["constraint"] == "unique"

    def test_structured_error_with_field_only(self):
        """When only field is provided, constraint should be absent."""
        with pytest.raises(HTTPException) as exc_info:
            validate(False, "Invalid", 400, field="email")
        detail = exc_info.value.detail
        assert isinstance(detail, dict)
        assert detail["field"] == "email"
        assert "constraint" not in detail


class TestHashPassword:
    """Tests for password hashing."""

    def test_returns_bcrypt_hash(self):
        """Hashed password should start with bcrypt prefix."""
        result = hash_password("mysecretpassword")
        assert result.startswith("$2b$")

    def test_different_hashes_for_same_password(self):
        """Two hashes of the same password should differ (unique salts)."""
        hash1 = hash_password("samepassword")
        hash2 = hash_password("samepassword")
        assert hash1 != hash2

    def test_hash_is_string(self):
        """Hash should be a string, not bytes."""
        result = hash_password("test")
        assert isinstance(result, str)


class TestVerifyPassword:
    """Tests for password verification."""

    def test_correct_password_verifies(self):
        """Correct password should return True."""
        hashed = hash_password("correctpassword")
        assert verify_password("correctpassword", hashed) is True

    def test_wrong_password_fails(self):
        """Wrong password should return False."""
        hashed = hash_password("correctpassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_empty_password_fails(self):
        """Empty password should not match a non-empty hash."""
        hashed = hash_password("notempty")
        assert verify_password("", hashed) is False


class TestGenerateAndDecodeTokens:
    """Tests for JWT token generation and decoding.

    These tests require RSA keys to be loaded, so we mock the
    signing/verifying bytes with a test key pair.
    """

    @pytest.fixture(autouse=True)
    def setup_test_keys(self):
        """Generate test RSA keys for token operations."""
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa

        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048
        )
        public_key = private_key.public_key()

        test_signing = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
        test_verifying = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        # Patch the module-level key bytes
        self._signing_patch = patch(
            "src.services.signing_bytes", test_signing
        )
        self._verifying_patch = patch(
            "src.services.verifying_bytes", test_verifying
        )
        self._signing_patch.start()
        self._verifying_patch.start()

        yield

        self._signing_patch.stop()
        self._verifying_patch.stop()

    def _make_mock_user(self, badge="EMP001", scopes=None):
        """Create a mock User with auth roles and permissions."""
        if scopes is None:
            scopes = ["employee.read", "timeclock.create"]

        permissions = []
        for scope in scopes:
            perm = Mock()
            perm.resource = scope
            permissions.append(perm)

        role = Mock()
        role.permissions = permissions

        user = Mock()
        user.badge_number = badge
        user.auth_roles = [role]
        return user

    def test_generate_access_token_contains_badge(self):
        """Access token payload should contain the badge number."""
        from src.services import decode_jwt_token, generate_access_token

        user = self._make_mock_user(badge="TEST001")
        token = generate_access_token(user)
        payload = decode_jwt_token(token)
        assert payload["badge_number"] == "TEST001"

    def test_generate_access_token_contains_scopes(self):
        """Access token payload should contain user scopes."""
        from src.services import decode_jwt_token, generate_access_token

        user = self._make_mock_user(scopes=["employee.read"])
        token = generate_access_token(user)
        payload = decode_jwt_token(token)
        assert "employee.read" in payload["scopes"]

    def test_generate_access_token_has_expiration(self):
        """Access token should have an exp claim."""
        from src.services import decode_jwt_token, generate_access_token

        user = self._make_mock_user()
        token = generate_access_token(user)
        payload = decode_jwt_token(token)
        assert "exp" in payload

    def test_generate_refresh_token_contains_badge(self):
        """Refresh token payload should contain the badge number."""
        from src.services import decode_jwt_token, generate_refresh_token

        user = self._make_mock_user(badge="REF001")
        token = generate_refresh_token(user)
        payload = decode_jwt_token(token)
        assert payload["badge_number"] == "REF001"

    def test_decode_adds_sub_field(self):
        """Decoded token should have a 'sub' field matching badge_number."""
        from src.services import decode_jwt_token, generate_access_token

        user = self._make_mock_user(badge="SUB001")
        token = generate_access_token(user)
        payload = decode_jwt_token(token)
        assert payload["sub"] == "SUB001"

    def test_decode_expired_token_raises(self):
        """Decoding an expired token should raise an exception."""
        import jwt as pyjwt

        from src.services import decode_jwt_token, encode_jwt_token

        expired = datetime.now(timezone.utc) - timedelta(hours=1)
        token = encode_jwt_token("EXP001", expired, [])
        with pytest.raises(pyjwt.ExpiredSignatureError):
            decode_jwt_token(token)

    def test_decode_invalid_token_raises(self):
        """Decoding a garbage token should raise an exception."""
        import jwt as pyjwt

        from src.services import decode_jwt_token

        with pytest.raises(pyjwt.InvalidTokenError):
            decode_jwt_token("not.a.valid.token")

    def test_encode_jwt_token_roundtrips(self):
        """encode_jwt_token and decode_jwt_token should roundtrip."""
        from src.services import decode_jwt_token, encode_jwt_token

        exp = datetime.now(timezone.utc) + timedelta(hours=1)
        token = encode_jwt_token("RT001", exp, ["a.read", "b.write"])
        payload = decode_jwt_token(token)
        assert payload["badge_number"] == "RT001"
        assert "a.read" in payload["scopes"]
        assert "b.write" in payload["scopes"]


class TestGetScopesFromUser:
    """Tests for get_scopes_from_user."""

    def test_user_with_no_roles(self):
        """User with no auth roles should have empty scopes."""
        user = Mock()
        user.auth_roles = []
        result = get_scopes_from_user(user)
        assert result == []

    def test_user_with_single_role(self):
        """User with one role should have that role's permissions."""
        perm1 = Mock()
        perm1.resource = "employee.read"
        perm2 = Mock()
        perm2.resource = "employee.create"

        role = Mock()
        role.permissions = [perm1, perm2]

        user = Mock()
        user.auth_roles = [role]

        result = get_scopes_from_user(user)
        assert set(result) == {"employee.read", "employee.create"}

    def test_user_with_multiple_roles_deduplicates(self):
        """Overlapping permissions across roles should be deduplicated."""
        perm_read = Mock()
        perm_read.resource = "employee.read"
        perm_create = Mock()
        perm_create.resource = "employee.create"
        perm_read2 = Mock()
        perm_read2.resource = "employee.read"  # duplicate

        role1 = Mock()
        role1.permissions = [perm_read, perm_create]
        role2 = Mock()
        role2.permissions = [perm_read2]

        user = Mock()
        user.auth_roles = [role1, role2]

        result = get_scopes_from_user(user)
        assert set(result) == {"employee.read", "employee.create"}
        # Should not contain duplicates
        assert len(result) == 2


class TestCreateEventLog:
    """Tests for create_event_log."""

    def test_creates_event_log_entry(self):
        """Should create and commit an EventLog with formatted message."""
        mock_db = MagicMock()

        with patch("src.services.EVENT_LOG_MSGS", {
            "employee": {"CREATE": "Employee {name} created"}
        }):
            create_event_log(
                identifier="employee",
                action="CREATE",
                log_args={"name": "John Doe"},
                caller_badge="0",
                db=mock_db,
            )

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

        event_log = mock_db.add.call_args[0][0]
        assert event_log.log == "Employee John Doe created"
        assert event_log.badge_number == "0"

    def test_event_log_with_multiple_args(self):
        """Should format message with multiple template args."""
        mock_db = MagicMock()

        with patch("src.services.EVENT_LOG_MSGS", {
            "department": {
                "ADD_MEMBER": "Employee {badge} added to {dept_name}"
            }
        }):
            create_event_log(
                identifier="department",
                action="ADD_MEMBER",
                log_args={"badge": "EMP001", "dept_name": "Engineering"},
                caller_badge="ADMIN",
                db=mock_db,
            )

        event_log = mock_db.add.call_args[0][0]
        assert event_log.log == "Employee EMP001 added to Engineering"


class TestLicenseActivationState:
    """Tests for license activation state management."""

    def test_set_license_activated_true(self):
        """Setting license activated to True should update global state."""
        from src.services import set_license_activated

        with patch("src.services.is_license_activated", False):
            set_license_activated(True)
            # The function sets the global directly
            import src.services
            assert src.services.is_license_activated is True

    def test_requires_license_raises_when_not_activated(self):
        """requires_license should raise 403 when license is not active."""
        from src.services import requires_license

        with patch("src.services.is_license_activated", False):
            mock_db = MagicMock()
            with pytest.raises(HTTPException) as exc_info:
                requires_license(db=mock_db)
            assert exc_info.value.status_code == 403

    def test_requires_license_passes_when_activated(self):
        """requires_license should not raise when license is active."""
        from src.services import requires_license

        with patch("src.services.is_license_activated", True):
            mock_db = MagicMock()
            # Should not raise
            requires_license(db=mock_db)
