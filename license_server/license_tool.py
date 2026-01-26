#!/usr/bin/env python3
"""TEP License Server - CLI tool for license management.

This standalone CLI tool allows administrators to:
- Generate new Ed25519 key pairs
- Create licenses (via API or directly)
- List all licenses
- Verify activations

Usage:
    python license_tool.py generate-keys
    python license_tool.py create-license [--customer "Name"]
    python license_tool.py list-licenses
    python license_tool.py convert <license_key>

The private key must be kept secure and never shared.
The public key should be embedded in the main application.
"""

import argparse
import sys
from pathlib import Path

from key_generator import (
    generate_key_pair,
    generate_unique_license_key,
    hex_to_words,
    normalize_license_key,
    words_to_hex,
)


def cmd_generate_keys(args: argparse.Namespace) -> None:
    """Generate a new Ed25519 key pair."""
    private_pem, public_pem = generate_key_pair()

    private_key_file = args.private_key or "private_key.pem"
    public_key_file = args.public_key or "public_key.pem"

    # Save private key
    with open(private_key_file, "wb") as f:
        f.write(private_pem)
    print(f"Private key saved to: {private_key_file}")
    print("  IMPORTANT: Keep this file secure and never share it!")

    # Save public key
    with open(public_key_file, "wb") as f:
        f.write(public_pem)
    print(f"Public key saved to: {public_key_file}")

    # Also print public key for embedding in application
    print("\nPublic key PEM (for embedding in the main application):")
    print("-" * 60)
    print(public_pem.decode("utf-8"))
    print("-" * 60)
    print("\nCopy this public key to:")
    print("  1. license_server/key_generator.py (PUBLIC_KEY_PEM)")
    print("  2. src/license/key_generator.py in the main TEP application")


def cmd_create_license(args: argparse.Namespace) -> None:
    """Create a new license key."""
    use_hex = args.hex

    print("Generating new license key...")
    print()

    license_key = generate_unique_license_key(word_format=not use_hex)

    print("License Key:")
    print("=" * 70)
    if use_hex:
        print(license_key)
    else:
        # Format word-based key nicely (4 groups per line)
        groups = license_key.split(" ")
        for i in range(0, len(groups), 4):
            print(" ".join(groups[i : i + 4]))
    print("=" * 70)

    # Also show hex format if word format was generated
    if not use_hex:
        hex_key = words_to_hex(license_key)
        print(f"\nHex format: {hex_key}")

    print("\nNote: This license key needs to be added to the license server database")
    print("      before it can be activated by clients.")
    print("\nTo add via API (when server is running):")
    print(f'  curl -X POST http://localhost:8001/api/licenses -H "Content-Type: application/json" \\')
    print(f'       -d \'{{"customer_name": "{args.customer or "Customer"}"}}\'')


def cmd_list_licenses(args: argparse.Namespace) -> None:
    """List all licenses (requires database access)."""
    try:
        from database import SessionLocal
        from models import Activation, License
    except ImportError:
        print("Error: Could not import database modules.")
        print("Make sure you're running from the license_server directory.")
        sys.exit(1)

    db = SessionLocal()
    try:
        licenses = db.query(License).all()

        if not licenses:
            print("No licenses found.")
            return

        print(f"Found {len(licenses)} license(s):\n")
        print("-" * 80)

        for lic in licenses:
            activations = db.query(Activation).filter(
                Activation.license_id == lic.id,
                Activation.is_active == True
            ).count()

            status = "ACTIVE" if lic.is_active else "REVOKED"
            print(f"ID: {lic.id}")
            print(f"  Key: {lic.license_key[:32]}...")
            print(f"  Customer: {lic.customer_name or 'N/A'}")
            print(f"  Status: {status}")
            print(f"  Created: {lic.created_at}")
            print(f"  Active Activations: {activations}")
            if lic.notes:
                print(f"  Notes: {lic.notes}")
            print("-" * 80)

    finally:
        db.close()


def cmd_convert(args: argparse.Namespace) -> None:
    """Convert license between word and hex formats."""
    license_key = args.license_key.strip()

    # Detect format and convert
    if len(license_key) == 128 and all(c in "0123456789abcdefABCDEF" for c in license_key):
        # Hex format -> word format
        print("Converting from hex to word format:")
        print()
        word_key = hex_to_words(license_key)
        groups = word_key.split(" ")
        for i in range(0, len(groups), 4):
            print(" ".join(groups[i : i + 4]))
    else:
        # Word format -> hex format
        print("Converting from word to hex format:")
        print()
        hex_key = words_to_hex(license_key)
        print(hex_key)


def cmd_init_db(args: argparse.Namespace) -> None:
    """Initialize the database."""
    try:
        from database import init_db
        init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point for the license tool."""
    parser = argparse.ArgumentParser(
        description="TEP License Server - License Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Generate a new key pair:
    python license_tool.py generate-keys

  Create a new license key:
    python license_tool.py create-license --customer "Acme Corp"

  List all licenses:
    python license_tool.py list-licenses

  Convert between formats:
    python license_tool.py convert "WORD-WORD-..."
    python license_tool.py convert abc123def456...

  Initialize database:
    python license_tool.py init-db

Note:
  Run 'generate-keys' first before starting the license server.
  The private_key.pem file must be in the license_server directory.
        """,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # generate-keys command
    keys_parser = subparsers.add_parser(
        "generate-keys",
        help="Generate a new Ed25519 key pair",
    )
    keys_parser.add_argument(
        "--private-key",
        help="Output file for private key (default: private_key.pem)",
    )
    keys_parser.add_argument(
        "--public-key",
        help="Output file for public key (default: public_key.pem)",
    )
    keys_parser.set_defaults(func=cmd_generate_keys)

    # create-license command
    license_parser = subparsers.add_parser(
        "create-license",
        help="Create a new license key",
    )
    license_parser.add_argument(
        "--customer",
        help="Customer name for this license",
    )
    license_parser.add_argument(
        "--hex",
        action="store_true",
        help="Output in hex format instead of word format",
    )
    license_parser.set_defaults(func=cmd_create_license)

    # list-licenses command
    list_parser = subparsers.add_parser(
        "list-licenses",
        help="List all licenses in the database",
    )
    list_parser.set_defaults(func=cmd_list_licenses)

    # convert command
    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert license between word and hex formats",
    )
    convert_parser.add_argument(
        "license_key",
        help="The license key to convert",
    )
    convert_parser.set_defaults(func=cmd_convert)

    # init-db command
    init_parser = subparsers.add_parser(
        "init-db",
        help="Initialize the database",
    )
    init_parser.set_defaults(func=cmd_init_db)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
