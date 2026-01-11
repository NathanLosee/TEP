"""Module for license key generation and validation.

This module handles:
- License key format validation
- Cryptographic signature verification using Ed25519
- License key generation (for separate licensing tool)

License key format: WORD-WORD-WORD-NN-WORD-WORD-WORD-NN
Example: EAGLE-RIVER-MOUNTAIN-42-TIGER-CLOUD-JADE-88
"""

import random
from typing import Tuple

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

# Word list for generating memorable license keys (same as device UUIDs)
WORD_LIST = [
    "APPLE", "BEACH", "CLOUD", "DELTA", "EAGLE", "FLAME", "GRASS", "HOUSE",
    "IVORY", "JADE", "KITE", "LIGHT", "MOON", "NIGHT", "OCEAN", "PEARL",
    "QUIET", "RIVER", "STONE", "TIGER", "ULTRA", "VENUS", "WATER", "XENON",
    "YOUTH", "ZEBRA", "AMBER", "BLADE", "CEDAR", "DUNE", "EMBER", "FROST",
    "GROVE", "HAWK", "IRIS", "JET", "KING", "LOTUS", "MIST", "NOVA",
    "OPAL", "PINE", "QUARTZ", "RAVEN", "SAGE", "THORN", "UNITY", "VINE",
    "WOLF", "XRAY", "YELLOW", "ZINC", "ARCTIC", "BLAZE", "CORAL", "DAWN",
    "ECHO", "FLARE", "GLOW", "HALO", "ICE", "JADE", "KELP", "LAVA",
    "MAPLE", "NECTAR", "ORBIT", "PRISM", "QUEST", "RIDGE", "SOLAR", "TIDE",
    "URBAN", "VORTEX", "WHALE", "XYLEM", "YARN", "ZENITH", "AZURE", "BRICK",
    "CRISP", "DREAM", "EDGE", "FIELD", "GRAIN", "HAVEN", "ISLAND", "JEWEL",
    "KNIGHT", "LAKE", "MEADOW", "NORTH", "OLIVE", "PLAIN", "QUEST", "RANGE",
    "SLOPE", "TRAIL", "UNION", "VALLEY", "WAVE", "YIELD", "ZONE", "ARCH",
    "BOLT", "CAPE", "DRIFT", "EARTH", "FLASH", "GATE", "HAVEN", "INLET",
    "JADE", "KNOT", "LEAF", "MOUNT", "NORTH", "ORBIT", "PEAK", "QUIET",
    "ROCKY", "SHORE", "TOWER", "UPPER", "VISTA", "WEST", "YACHT", "ZEAL"
]

# Public key for signature verification (embedded in application)
# This is a placeholder - you'll generate your own key pair
PUBLIC_KEY_PEM = b"""-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAGb9ECWmEzf6FQbrBZ9w7lshQhqoWTT8pSNlLJT3cT8E=
-----END PUBLIC KEY-----"""


def generate_license_key() -> str:
    """Generate a human-readable license key.

    Format: WORD1-WORD2-WORD3-NN-WORD4-WORD5-WORD6-NN

    Returns:
        str: A license key like "EAGLE-RIVER-MOUNTAIN-42-TIGER-CLOUD-JADE-88"

    Note:
        This function is intended for use in a separate license generation tool,
        not within the main application.
    """
    # Select 6 random words
    words = random.sample(WORD_LIST, 6)

    # Generate 2 random numbers between 10 and 99
    num1 = random.randint(10, 99)
    num2 = random.randint(10, 99)

    # Combine into license key format
    return f"{words[0]}-{words[1]}-{words[2]}-{num1}-{words[3]}-{words[4]}-{words[5]}-{num2}"


def validate_license_key_format(license_key: str) -> bool:
    """Validate that a license key matches the expected format.

    Args:
        license_key: The license key string to validate

    Returns:
        bool: True if the license key matches format WORD-WORD-WORD-NN-WORD-WORD-WORD-NN
    """
    parts = license_key.split("-")

    # Must have exactly 8 parts
    if len(parts) != 8:
        return False

    # Check pattern: word, word, word, number, word, word, word, number
    expected_pattern = [True, True, True, False, True, True, True, False]

    for i, is_word in enumerate(expected_pattern):
        if is_word:
            # Should be uppercase letters
            if not parts[i].isupper() or not parts[i].isalpha():
                return False
        else:
            # Should be a 2-digit number
            if not parts[i].isdigit() or len(parts[i]) != 2:
                return False

    return True


def verify_license_signature(license_key: str, signature: str) -> bool:
    """Verify the cryptographic signature of a license key.

    Args:
        license_key: The license key to verify
        signature: The signature string (hex-encoded)

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
        signature_bytes = bytes.fromhex(signature)

        # Verify signature
        public_key.verify(signature_bytes, license_key.encode("utf-8"))
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


def sign_license_key(license_key: str, private_key_pem: bytes) -> str:
    """Sign a license key with a private key.

    Args:
        license_key: The license key to sign
        private_key_pem: The private key in PEM format

    Returns:
        str: Hex-encoded signature

    Note:
        This function is for use in your separate license generation tool.
        The private key should never be embedded in the application.
    """
    # Load private key
    private_key = serialization.load_pem_private_key(private_key_pem, password=None)
    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("Invalid private key type")

    # Sign the license key
    signature = private_key.sign(license_key.encode("utf-8"))

    # Return as hex string
    return signature.hex()
