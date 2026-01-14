"""Module for license key generation and validation.

This module handles:
- License key format validation (Ed25519 signature in hex format)
- Cryptographic signature verification using Ed25519
- License key generation (for separate licensing tool)

The license key IS the Ed25519 signature itself (hex-encoded, 128 characters).
This eliminates the need for separate key + signature fields.
"""

from typing import Tuple

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

# Public key for signature verification (embedded in application)
# This is a placeholder - you'll generate your own key pair
PUBLIC_KEY_PEM = b"""-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAGb9ECWmEzf6FQbrBZ9w7lshQhqoWTT8pSNlLJT3cT8E=
-----END PUBLIC KEY-----"""

# Message that gets signed to create the license key
# This should be a constant unique to your application
LICENSE_MESSAGE = b"TEP-License-v1"


def generate_license_key(private_key_pem: bytes) -> str:
    """Generate a license key by signing the standard license message.

    Args:
        private_key_pem: The private key in PEM format

    Returns:
        str: The Ed25519 signature in hex format (128 characters)

    Note:
        This function is intended for use in a separate license generation tool,
        not within the main application. The private key should never be
        embedded in the application.
    """
    # Load private key
    private_key = serialization.load_pem_private_key(private_key_pem, password=None)
    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("Invalid private key type")

    # Sign the standard license message
    signature = private_key.sign(LICENSE_MESSAGE)

    # Return as hex string
    return signature.hex()


def validate_license_key_format(license_key: str) -> bool:
    """Validate that a license key matches the expected format.

    Args:
        license_key: The license key string to validate (hex-encoded Ed25519 signature)

    Returns:
        bool: True if the license key is a valid hex string of correct length (128 chars)
    """
    # Ed25519 signatures are 64 bytes, which is 128 hex characters
    if len(license_key) != 128:
        return False

    # Must be valid hexadecimal
    try:
        bytes.fromhex(license_key)
        return True
    except ValueError:
        return False


def verify_license_key(license_key: str) -> bool:
    """Verify the cryptographic signature that serves as the license key.

    Args:
        license_key: The license key (hex-encoded Ed25519 signature) to verify

    Returns:
        bool: True if the signature is valid

    Raises:
        ValueError: If signature format is invalid
    """
    try:
        # Load public key
        public_key = serialization.load_pem_public_key(PUBLIC_KEY_PEM)
        if not isinstance(public_key, Ed25519PublicKey):
            raise ValueError("Invalid public key type")

        # Decode signature from hex
        signature_bytes = bytes.fromhex(license_key)

        # Verify signature against the standard license message
        public_key.verify(signature_bytes, LICENSE_MESSAGE)
        return True

    except (InvalidSignature, ValueError):
        return False


def generate_key_pair() -> Tuple[bytes, bytes]:
    """Generate a new Ed25519 key pair for license signing.

    This function is for generating the initial key pair. The private key
    should be kept secure and used only in your license generation tool.
    The public key should replace PUBLIC_KEY_PEM in this file.

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
        encryption_algorithm=serialization.NoEncryption()
    )

    # Get public key
    public_key = private_key.public_key()

    # Serialize public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return (private_pem, public_pem)


