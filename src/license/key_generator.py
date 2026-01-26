"""Module for license key validation and activation verification.

This module handles:
- License key format validation (word-based or hex format)
- Activation key verification using Ed25519 signatures
- Human-readable word encoding/decoding
- Machine ID retrieval for hardware binding

License Flow:
1. User enters a license_key (obtained from license server admin)
2. Client sends license_key + machine_id to license server
3. License server returns activation_key (signed proof)
4. Client stores license_key + activation_key locally
5. On startup, client verifies activation_key matches its machine_id

License keys can be in two formats:
1. Word format: WORD-WORD-WORD-WORD-...-WORD (64 words, easier to type)
2. Hex format: 128-character hex string (compact)
"""

from pathlib import Path
from typing import List, Optional

import machineid
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

# Public key for activation signature verification
# This must match the key used by the license server
# Generate with: python license_tool.py generate-keys
PUBLIC_KEY_PEM = b"""-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAG+75HW6g1TbJNZQDMR26D/vWszI9aYF/QUQHr+6tg4s=
-----END PUBLIC KEY-----"""

# Message prefix for activation key signatures (must match license server)
ACTIVATION_MESSAGE_PREFIX = b"TEP-Activation-v2:"


def get_machine_id() -> str:
    """Get the current machine's unique identifier.

    This is used internally for license activation and should not
    be exposed to users.

    Returns:
        str: The machine's unique ID (hashed for privacy).
    """
    return machineid.hashed_id("TEP-License")


def get_activation_message(license_key: str, machine_id: str) -> bytes:
    """Get the message that was signed for an activation.

    Args:
        license_key: The license key (hex format).
        machine_id: The machine's unique identifier.

    Returns:
        bytes: The message that should have been signed.
    """
    return ACTIVATION_MESSAGE_PREFIX + f"{license_key}:{machine_id}".encode("utf-8")


def _load_word_list() -> List[str]:
    """Load word list from words.txt file.

    Returns:
        list[str]: List of uppercase words
    """
    words_file = Path(__file__).parent.parent.parent / "words.txt"
    with open(words_file, "r", encoding="utf-8") as f:
        return [line.strip().upper() for line in f if line.strip()]


# Load word list - we need exactly 256 words for 1-byte-per-word encoding
_FULL_WORD_LIST = _load_word_list()
WORD_LIST = _FULL_WORD_LIST[:256] if len(_FULL_WORD_LIST) >= 256 else _FULL_WORD_LIST

# Create reverse lookup
WORD_TO_INDEX = {word: i for i, word in enumerate(WORD_LIST)}


def hex_to_words(hex_key: str) -> str:
    """Convert a hex license key to word format.

    Each byte (00-FF) maps to one word from the 256-word list.
    64 bytes = 64 words, grouped as 16 groups of 4 words each.

    Args:
        hex_key: 128-character hex string

    Returns:
        str: Word-based key in format "WORD-WORD-WORD-WORD WORD-WORD-WORD-WORD ..."
    """
    if len(hex_key) != 128:
        raise ValueError("Hex key must be 128 characters")

    key_bytes = bytes.fromhex(hex_key)
    words = [WORD_LIST[b] for b in key_bytes]

    groups = []
    for i in range(0, 64, 4):
        group = "-".join(words[i : i + 4])
        groups.append(group)

    return " ".join(groups)


def words_to_hex(word_key: str) -> str:
    """Convert a word-based license key to hex format.

    Args:
        word_key: Word-based key (groups separated by spaces, words by dashes)

    Returns:
        str: 128-character hex string

    Raises:
        ValueError: If the word format is invalid or contains unknown words
    """
    word_key = word_key.upper().strip()

    if " " in word_key:
        groups = word_key.split()
        words = []
        for group in groups:
            words.extend(group.split("-"))
    else:
        words = word_key.split("-")

    words = [w for w in words if w]

    if len(words) != 64:
        raise ValueError(f"Word key must contain exactly 64 words, got {len(words)}")

    key_bytes = bytearray()
    for word in words:
        if word not in WORD_TO_INDEX:
            raise ValueError(f"Unknown word in license key: {word}")
        key_bytes.append(WORD_TO_INDEX[word])

    return key_bytes.hex()


def is_word_format(license_key: str) -> bool:
    """Check if a license key is in word format.

    Args:
        license_key: The license key to check

    Returns:
        bool: True if the key appears to be in word format
    """
    normalized = license_key.upper().strip()

    if len(normalized) == 128:
        try:
            bytes.fromhex(normalized)
            return False
        except ValueError:
            pass

    return "-" in normalized or " " in normalized


def normalize_license_key(license_key: str) -> str:
    """Normalize a license key to hex format.

    Accepts both word format and hex format, returns hex format.

    Args:
        license_key: License key in either format

    Returns:
        str: 128-character hex string
    """
    license_key = license_key.strip()

    if is_word_format(license_key):
        return words_to_hex(license_key)
    else:
        return license_key.lower()


def validate_license_key_format(license_key: str) -> bool:
    """Validate that a license key matches the expected format.

    Accepts both word format and hex format.

    Args:
        license_key: The license key string to validate

    Returns:
        bool: True if the license key is valid format
    """
    try:
        normalized = normalize_license_key(license_key)
        if len(normalized) != 128:
            return False
        bytes.fromhex(normalized)
        return True
    except (ValueError, KeyError):
        return False


def verify_activation_key(
    license_key: str,
    activation_key: Optional[str],
    machine_id: Optional[str] = None,
) -> bool:
    """Verify an activation key is valid for this machine.

    This verifies that the activation_key is a valid signature of
    (license_key + machine_id) using the license server's public key.

    Args:
        license_key: The license key (word or hex format).
        activation_key: The activation key from the license server (hex format).
        machine_id: The machine ID to verify against. If None, uses current machine.

    Returns:
        bool: True if the activation is valid for this license and machine.
    """
    try:
        # Activation key is required
        if not activation_key:
            return False

        # Normalize license key to hex format
        normalized_license = normalize_license_key(license_key)

        # Use current machine ID if not provided
        if machine_id is None:
            machine_id = get_machine_id()

        # Load public key
        public_key = serialization.load_pem_public_key(PUBLIC_KEY_PEM)
        if not isinstance(public_key, Ed25519PublicKey):
            raise ValueError("Invalid public key type")

        # Decode activation key from hex
        signature_bytes = bytes.fromhex(activation_key)

        # Verify signature against the activation message
        message = get_activation_message(normalized_license, machine_id)
        public_key.verify(signature_bytes, message)
        return True

    except (InvalidSignature, ValueError, KeyError, TypeError):
        return False
