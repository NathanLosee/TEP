"""Unit tests for license key generator functions."""

from unittest.mock import MagicMock, patch

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from src.license.key_generator import (
    WORD_LIST,
    WORD_TO_INDEX,
    get_activation_message,
    get_machine_id,
    hex_to_words,
    is_word_format,
    normalize_license_key,
    validate_license_key_format,
    verify_activation_key,
    words_to_hex,
)


class TestWordList:
    """Tests for the word list loading."""

    def test_word_list_has_256_entries(self):
        """Word list must have exactly 256 entries for byte encoding."""
        assert len(WORD_LIST) == 256

    def test_word_list_entries_are_uppercase(self):
        """All words in the list should be uppercase."""
        for word in WORD_LIST:
            assert word == word.upper(), f"Word '{word}' is not uppercase"

    def test_word_to_index_matches_word_list(self):
        """Reverse lookup should match forward lookup."""
        for i, word in enumerate(WORD_LIST):
            assert WORD_TO_INDEX[word] == i


class TestHexToWords:
    """Tests for hex_to_words conversion."""

    def test_valid_hex_converts_to_words(self):
        """A valid 128-char hex string should produce 64 words."""
        hex_key = "00" * 64  # All zeros -> first word repeated
        result = hex_to_words(hex_key)
        words = []
        for group in result.split(" "):
            words.extend(group.split("-"))
        assert len(words) == 64
        # All bytes are 0x00, so all words should be the first word
        assert all(w == WORD_LIST[0] for w in words)

    def test_sequential_bytes_map_to_different_words(self):
        """Each unique byte value should map to a different word."""
        # Use bytes 0-63, each repeated once to fill 128 hex chars
        hex_key = "".join(f"{i:02x}" for i in range(64))
        result = hex_to_words(hex_key)
        words = []
        for group in result.split(" "):
            words.extend(group.split("-"))
        # First 64 words should map to first 64 words in list
        for i in range(64):
            assert words[i] == WORD_LIST[i]

    def test_invalid_hex_length_raises_error(self):
        """Hex key with wrong length should raise ValueError."""
        with pytest.raises(ValueError, match="128 characters"):
            hex_to_words("abcdef")

    def test_output_format_has_groups(self):
        """Output should have 16 groups of 4 words separated by spaces."""
        hex_key = "ab" * 64
        result = hex_to_words(hex_key)
        groups = result.split(" ")
        assert len(groups) == 16
        for group in groups:
            assert len(group.split("-")) == 4


class TestWordsToHex:
    """Tests for words_to_hex conversion."""

    def test_valid_words_convert_to_hex(self):
        """Valid 64-word key should produce 128-char hex string."""
        # Use first word repeated 64 times (maps to 0x00)
        word_key = "-".join([WORD_LIST[0]] * 64)
        result = words_to_hex(word_key)
        assert len(result) == 128
        assert result == "00" * 64

    def test_grouped_words_convert_correctly(self):
        """Words with space-separated groups should also work."""
        words = [WORD_LIST[0]] * 64
        groups = []
        for i in range(0, 64, 4):
            groups.append("-".join(words[i:i + 4]))
        word_key = " ".join(groups)
        result = words_to_hex(word_key)
        assert len(result) == 128

    def test_wrong_word_count_raises_error(self):
        """Non-64 word input should raise ValueError."""
        word_key = "-".join([WORD_LIST[0]] * 10)
        with pytest.raises(ValueError, match="64 words"):
            words_to_hex(word_key)

    def test_unknown_word_raises_error(self):
        """Unknown word should raise ValueError."""
        words = [WORD_LIST[0]] * 63 + ["ZZZZNOTAWORD"]
        word_key = "-".join(words)
        with pytest.raises(ValueError, match="Unknown word"):
            words_to_hex(word_key)

    def test_case_insensitive(self):
        """Conversion should be case-insensitive."""
        word_key = "-".join([WORD_LIST[0].lower()] * 64)
        result = words_to_hex(word_key)
        assert len(result) == 128


class TestHexWordsRoundtrip:
    """Tests for roundtrip conversion between hex and word formats."""

    def test_hex_to_words_to_hex(self):
        """Converting hex->words->hex should return original."""
        original = "ab" * 64
        word_form = hex_to_words(original)
        recovered = words_to_hex(word_form)
        assert recovered == original

    def test_all_byte_values(self):
        """All 256 byte values should roundtrip correctly."""
        # Use bytes 0-63 to fill exactly 64 bytes
        hex_key = "".join(f"{i:02x}" for i in range(64))
        word_form = hex_to_words(hex_key)
        recovered = words_to_hex(word_form)
        assert recovered == hex_key


class TestIsWordFormat:
    """Tests for is_word_format detection."""

    def test_hex_string_is_not_word_format(self):
        """A 128-char hex string should not be detected as word format."""
        hex_key = "ab" * 64
        assert is_word_format(hex_key) is False

    def test_dash_separated_words_are_word_format(self):
        """Dash-separated words should be detected as word format."""
        word_key = "-".join([WORD_LIST[0]] * 64)
        assert is_word_format(word_key) is True

    def test_space_separated_groups_are_word_format(self):
        """Space-separated groups should be detected as word format."""
        words = [WORD_LIST[0]] * 64
        groups = []
        for i in range(0, 64, 4):
            groups.append("-".join(words[i:i + 4]))
        word_key = " ".join(groups)
        assert is_word_format(word_key) is True

    def test_short_string_without_separators_is_not_word_format(self):
        """A short plain string without dashes/spaces is not word format."""
        assert is_word_format("abc123") is False


class TestNormalizeLicenseKey:
    """Tests for normalize_license_key."""

    def test_hex_passthrough(self):
        """Hex format should pass through in lowercase."""
        hex_key = "AB" * 64
        result = normalize_license_key(hex_key)
        assert result == "ab" * 64

    def test_word_to_hex_conversion(self):
        """Word format should be converted to hex."""
        hex_key = "00" * 64
        word_key = hex_to_words(hex_key)
        result = normalize_license_key(word_key)
        assert result == hex_key

    def test_strips_whitespace(self):
        """Leading/trailing whitespace should be stripped."""
        hex_key = "ab" * 64
        result = normalize_license_key(f"  {hex_key}  ")
        assert result == hex_key


class TestValidateLicenseKeyFormat:
    """Tests for validate_license_key_format."""

    def test_valid_hex_format(self):
        """Valid 128-char hex string should pass."""
        hex_key = "ab" * 64
        assert validate_license_key_format(hex_key) is True

    def test_valid_word_format(self):
        """Valid 64-word key should pass."""
        hex_key = "ab" * 64
        word_key = hex_to_words(hex_key)
        assert validate_license_key_format(word_key) is True

    def test_wrong_hex_length(self):
        """Hex string of wrong length should fail."""
        assert validate_license_key_format("abcdef") is False

    def test_invalid_hex_characters(self):
        """Non-hex characters should fail."""
        assert validate_license_key_format("zz" * 64) is False

    def test_empty_string(self):
        """Empty string should fail."""
        assert validate_license_key_format("") is False


class TestVerifyActivationKey:
    """Tests for verify_activation_key with Ed25519 signatures."""

    @pytest.fixture
    def ed25519_keypair(self):
        """Generate a fresh Ed25519 key pair for testing."""
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        return private_key, public_key

    def test_valid_signature_verifies(self, ed25519_keypair):
        """A correctly signed activation key should verify."""
        private_key, public_key = ed25519_keypair
        license_key = "ab" * 64
        machine_id = "test-machine-id"

        message = get_activation_message(license_key, machine_id)
        signature = private_key.sign(message)
        activation_key = signature.hex()

        # Patch the PUBLIC_KEY_PEM to use our test key
        from cryptography.hazmat.primitives import serialization
        test_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        with patch("src.license.key_generator.PUBLIC_KEY_PEM", test_pem):
            result = verify_activation_key(
                license_key, activation_key, machine_id
            )
        assert result is True

    def test_invalid_signature_fails(self, ed25519_keypair):
        """An incorrect signature should fail verification."""
        _, public_key = ed25519_keypair
        license_key = "ab" * 64
        machine_id = "test-machine-id"
        bad_activation = "ff" * 64  # Random bytes, not a valid signature

        from cryptography.hazmat.primitives import serialization
        test_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        with patch("src.license.key_generator.PUBLIC_KEY_PEM", test_pem):
            result = verify_activation_key(
                license_key, bad_activation, machine_id
            )
        assert result is False

    def test_none_activation_key_fails(self):
        """None activation key should return False."""
        result = verify_activation_key("ab" * 64, None, "machine-id")
        assert result is False

    def test_empty_activation_key_fails(self):
        """Empty activation key should return False."""
        result = verify_activation_key("ab" * 64, "", "machine-id")
        assert result is False


class TestGetMachineId:
    """Tests for get_machine_id."""

    def test_returns_non_empty_string(self):
        """Machine ID should be a non-empty string."""
        result = get_machine_id()
        assert isinstance(result, str)
        assert len(result) > 0


class TestGetActivationMessage:
    """Tests for get_activation_message."""

    def test_message_contains_prefix(self):
        """Message should start with the activation prefix."""
        result = get_activation_message("testkey", "testmachine")
        assert result.startswith(b"TAP-Activation-v2:")

    def test_message_contains_key_and_machine(self):
        """Message should contain both license key and machine ID."""
        result = get_activation_message("mykey", "mymachine")
        assert b"mykey" in result
        assert b"mymachine" in result

    def test_message_format(self):
        """Message should be prefix + key:machine_id."""
        result = get_activation_message("key123", "machine456")
        expected = b"TAP-Activation-v2:key123:machine456"
        assert result == expected
