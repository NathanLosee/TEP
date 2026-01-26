"""Module for license key generation and validation.

This module handles:
- License key generation (random unique keys)
- Activation key generation (signing license_key + machine_id)
- Activation key verification
- Human-readable word encoding/decoding

License Flow:
1. License server generates a unique license_key for each customer
2. When client activates, it sends license_key + machine_id to server
3. Server signs (license_key + machine_id) to create activation_key
4. Client stores license_key + activation_key locally
5. On startup, client verifies activation_key matches its machine_id

License keys can be in two formats:
1. Word format: WORD-WORD-WORD-WORD-...-WORD (64 words, easier to type)
2. Hex format: 128-character hex string (compact)
"""

import secrets
from pathlib import Path
from typing import List, Optional, Tuple

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

# Public key for signature verification (embedded in main application)
# This is a placeholder - generate your own key pair with generate-keys command
PUBLIC_KEY_PEM = b"""-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEApSp2CAkKgzPYlRKbrf5Kg5V8f8yEQVzmues2M2zq4NQ=
-----END PUBLIC KEY-----"""

# Message prefix for activation key signatures
ACTIVATION_MESSAGE_PREFIX = b"TEP-Activation-v2:"


def get_activation_message(license_key: str, machine_id: str) -> bytes:
    """Get the message to sign for an activation.

    The activation message combines the license key and machine ID,
    ensuring the activation is bound to both.

    Args:
        license_key: The license key being activated.
        machine_id: The machine's unique identifier.

    Returns:
        bytes: The message to sign for activation.
    """
    return ACTIVATION_MESSAGE_PREFIX + f"{license_key}:{machine_id}".encode("utf-8")


def generate_unique_license_key(word_format: bool = True) -> str:
    """Generate a unique random license key.

    Creates a cryptographically random 64-byte key that serves as
    the unique license identifier. This does NOT require signing -
    it's just a unique identifier.

    Args:
        word_format: If True, return word-based format; if False, return hex format.

    Returns:
        str: The license key (word format or hex format).
    """
    # Generate 64 random bytes
    random_bytes = secrets.token_bytes(64)
    hex_key = random_bytes.hex()

    if word_format:
        return hex_to_words(hex_key)
    return hex_key


def _load_word_list() -> List[str]:
    """Load word list from words.txt file.

    Returns:
        list[str]: List of uppercase words
    """
    words_file = Path(__file__).parent / "words.txt"
    with open(words_file, "r", encoding="utf-8") as f:
        return [line.strip().upper() for line in f if line.strip()]


# Load word list - we need exactly 256 words for 1-byte-per-word encoding
# If we have more, we'll use the first 256
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
             (16 groups of 4 words, groups separated by spaces, words by dashes)
    """
    if len(hex_key) != 128:
        raise ValueError("Hex key must be 128 characters")

    # Convert hex to bytes
    key_bytes = bytes.fromhex(hex_key)

    # Convert each byte to a word
    words = [WORD_LIST[b] for b in key_bytes]

    # Group into 16 groups of 4 words
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
    # Normalize input - handle various separators
    word_key = word_key.upper().strip()

    # Split by spaces first (groups), then by dashes (words within groups)
    # Also handle the case where everything is dash-separated
    if " " in word_key:
        groups = word_key.split()
        words = []
        for group in groups:
            words.extend(group.split("-"))
    else:
        words = word_key.split("-")

    # Filter out empty strings
    words = [w for w in words if w]

    if len(words) != 64:
        raise ValueError(f"Word key must contain exactly 64 words, got {len(words)}")

    # Convert words back to bytes
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
    # Word format contains letters and dashes/spaces, but no hex-only characters
    normalized = license_key.upper().strip()

    # If it's 128 chars and all hex, it's hex format
    if len(normalized) == 128:
        try:
            bytes.fromhex(normalized)
            return False
        except ValueError:
            pass

    # Check if it contains typical word separators
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
        # Already hex format, just lowercase
        return license_key.lower()


def generate_activation_key(
    private_key_pem: bytes,
    license_key: str,
    machine_id: str,
) -> str:
    """Generate an activation key by signing the license_key + machine_id.

    This creates a cryptographic proof that the license is valid for
    the specific machine. The activation key can only be verified
    with the corresponding public key.

    Args:
        private_key_pem: The private key in PEM format.
        license_key: The license key being activated (hex format).
        machine_id: The machine's unique identifier.

    Returns:
        str: The activation key (128-character hex string).

    Note:
        This function should only be called by the license server.
        The private key must never be in the client application.
    """
    # Load private key
    private_key = serialization.load_pem_private_key(private_key_pem, password=None)
    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("Invalid private key type")

    # Sign the activation message (license_key + machine_id)
    message = get_activation_message(license_key, machine_id)
    signature = private_key.sign(message)

    return signature.hex()


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
        # License keys are 64 bytes, which is 128 hex characters
        if len(normalized) != 128:
            return False
        bytes.fromhex(normalized)
        return True
    except (ValueError, KeyError):
        return False


def verify_activation_key(
    license_key: str,
    machine_id: str,
    activation_key: str,
    public_key_pem: Optional[bytes] = None,
) -> bool:
    """Verify an activation key is valid for the given license and machine.

    This checks that the activation_key is a valid signature of
    (license_key + machine_id) using the license server's public key.

    Args:
        license_key: The license key (word or hex format).
        machine_id: The machine's unique identifier.
        activation_key: The activation key to verify (hex format).
        public_key_pem: Optional public key PEM. If None, uses the embedded key.

    Returns:
        bool: True if the activation is valid for this license and machine.
    """
    try:
        # Normalize license key to hex format
        normalized_license = normalize_license_key(license_key)

        # Load public key
        key_pem = public_key_pem or PUBLIC_KEY_PEM
        public_key = serialization.load_pem_public_key(key_pem)
        if not isinstance(public_key, Ed25519PublicKey):
            raise ValueError("Invalid public key type")

        # Decode activation key from hex
        signature_bytes = bytes.fromhex(activation_key)

        # Verify signature against the activation message
        message = get_activation_message(normalized_license, machine_id)
        public_key.verify(signature_bytes, message)
        return True

    except (InvalidSignature, ValueError, KeyError):
        return False


def generate_key_pair() -> Tuple[bytes, bytes]:
    """Generate a new Ed25519 key pair for license signing.

    This function is for generating the initial key pair. The private key
    should be kept secure and used only in your license generation tool.
    The public key should replace PUBLIC_KEY_PEM in this file and in the
    main application's key_generator.py.

    Returns:
        Tuple[bytes, bytes]: (private_key_pem, public_key_pem)

    Note:
        This function should only be used once to generate your key pair,
        not during normal application operation.
    """
    # Generate private key
    private_key = Ed25519PrivateKey.generate()

    # Serialize private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Get public key
    public_key = private_key.public_key()

    # Serialize public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return (private_pem, public_pem)
