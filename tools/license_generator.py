#!/usr/bin/env python3
"""License Key Generator for TAP.

This tool generates license keys for the TAP application using Ed25519
cryptographic signatures. The private key must be kept secure and never
distributed with the application.

Usage:
    python license_generator.py --generate-keypair
    python license_generator.py --generate-license --private-key private.pem
    python license_generator.py --verify-license <license_key> --public-key public.pem
"""

import argparse
import sys
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

# Standard message that gets signed to create license keys
LICENSE_MESSAGE = b"TAP-License-v1"


def generate_key_pair(output_dir: Path = Path(".")):
    """Generate a new Ed25519 key pair for license signing.

    Args:
        output_dir: Directory to save the key files

    Returns:
        tuple: (private_key_path, public_key_path)
    """
    print("Generating Ed25519 key pair...")

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

    # Save keys
    private_key_path = output_dir / "tap_private_key.pem"
    public_key_path = output_dir / "tap_public_key.pem"

    private_key_path.write_bytes(private_pem)
    public_key_path.write_bytes(public_pem)

    # Set restrictive permissions on private key (Unix-like systems)
    try:
        import os

        os.chmod(private_key_path, 0o600)
    except (ImportError, OSError):
        pass

    print(f"[OK] Private key saved to: {private_key_path}")
    print(f"[OK] Public key saved to: {public_key_path}")
    print()
    print("SECURITY WARNING:")
    print("  - Keep the private key SECURE and NEVER distribute it")
    print("  - The public key should be embedded in the application")
    print(
        f"  - Update src/license/key_generator.py with the public key from {public_key_path}"
    )
    print()

    return private_key_path, public_key_path


def generate_license_key(private_key_path: Path) -> str:
    """Generate a license key by signing the standard license message.

    Args:
        private_key_path: Path to the private key PEM file

    Returns:
        str: The Ed25519 signature in hex format (128 characters)
    """
    if not private_key_path.exists():
        raise FileNotFoundError(f"Private key not found: {private_key_path}")

    # Load private key
    private_key_pem = private_key_path.read_bytes()
    private_key = serialization.load_pem_private_key(
        private_key_pem, password=None
    )

    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("Invalid private key type - must be Ed25519")

    # Sign the standard license message
    signature = private_key.sign(LICENSE_MESSAGE)

    # Return as hex string
    return signature.hex()


def verify_license_key(license_key: str, public_key_path: Path) -> bool:
    """Verify a license key against the public key.

    Args:
        license_key: The license key (hex-encoded Ed25519 signature) to verify
        public_key_path: Path to the public key PEM file

    Returns:
        bool: True if the signature is valid
    """
    if not public_key_path.exists():
        raise FileNotFoundError(f"Public key not found: {public_key_path}")

    # Validate format
    if len(license_key) != 128:
        print(
            f"[FAIL] Invalid format: License key must be 128 characters (got {len(license_key)})"
        )
        return False

    try:
        bytes.fromhex(license_key)
    except ValueError:
        print("[FAIL] Invalid format: License key must be valid hexadecimal")
        return False

    # Load public key
    public_key_pem = public_key_path.read_bytes()
    public_key = serialization.load_pem_public_key(public_key_pem)

    if not isinstance(public_key, Ed25519PublicKey):
        raise ValueError("Invalid public key type - must be Ed25519")

    try:
        # Decode signature from hex
        signature_bytes = bytes.fromhex(license_key)

        # Verify signature against the standard license message
        public_key.verify(signature_bytes, LICENSE_MESSAGE)
        return True

    except (InvalidSignature, ValueError) as e:
        print(f"[FAIL] Verification failed: {e}")
        return False


def main():
    """Main entry point for the license generator tool."""
    parser = argparse.ArgumentParser(
        description="TAP License Key Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a new key pair (do this once)
  python license_generator.py --generate-keypair

  # Generate a single license key
  python license_generator.py --generate-license --private-key tap_private_key.pem

  # Generate multiple license keys
  python license_generator.py --generate-license --private-key tap_private_key.pem --count 10

  # Verify a license key
  python license_generator.py --verify-license <key> --public-key tap_public_key.pem
        """,
    )

    parser.add_argument(
        "--generate-keypair",
        action="store_true",
        help="Generate a new Ed25519 key pair",
    )

    parser.add_argument(
        "--generate-license",
        action="store_true",
        help="Generate license key(s)",
    )

    parser.add_argument(
        "--verify-license",
        type=str,
        metavar="KEY",
        help="Verify a license key",
    )

    parser.add_argument(
        "--private-key",
        type=Path,
        metavar="FILE",
        help="Path to private key PEM file",
    )

    parser.add_argument(
        "--public-key",
        type=Path,
        metavar="FILE",
        help="Path to public key PEM file",
    )

    parser.add_argument(
        "--count",
        type=int,
        default=1,
        metavar="N",
        help="Number of license keys to generate (default: 1)",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("."),
        metavar="DIR",
        help="Output directory for generated keys (default: current directory)",
    )

    args = parser.parse_args()

    # Validate arguments
    if not any(
        [args.generate_keypair, args.generate_license, args.verify_license]
    ):
        parser.print_help()
        sys.exit(1)

    try:
        # Generate key pair
        if args.generate_keypair:
            args.output_dir.mkdir(parents=True, exist_ok=True)
            generate_key_pair(args.output_dir)
            return 0

        # Generate license key(s)
        if args.generate_license:
            if not args.private_key:
                print(
                    "Error: --private-key is required for license generation"
                )
                return 1

            print(f"Generating {args.count} license key(s)...")
            print()

            for i in range(args.count):
                license_key = generate_license_key(args.private_key)
                print(f"License Key {i+1}:")
                print(f"  {license_key}")
                print()

            print(f"[OK] Generated {args.count} license key(s) successfully")
            return 0

        # Verify license key
        if args.verify_license:
            if not args.public_key:
                print(
                    "Error: --public-key is required for license verification"
                )
                return 1

            print(f"Verifying license key: {args.verify_license}")
            print()

            if verify_license_key(args.verify_license, args.public_key):
                print("[OK] License key is VALID")
                return 0
            else:
                print("[FAIL] License key is INVALID")
                return 1

    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
