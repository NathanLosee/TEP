#!/usr/bin/env python3
"""License tool for TEP application (DEPRECATED).

This tool has been deprecated. License management is now handled by
the license server at license_server/.

For license management, use the license server tools instead:
    cd license_server
    python license_tool.py --help

This file is kept for backwards compatibility with format conversion only.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.license.key_generator import (
    hex_to_words,
    words_to_hex,
)


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


def main() -> None:
    """Main entry point for the license tool."""
    parser = argparse.ArgumentParser(
        description="TEP License Tool (DEPRECATED - Use license_server/license_tool.py instead)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
DEPRECATED: This tool has been replaced by the license server.

For license management, use:
    cd license_server
    python license_tool.py --help

The only remaining functionality here is format conversion:
    python license_tool.py convert "WORD-WORD-..."
    python license_tool.py convert abc123def456...
        """,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # convert command (only remaining functionality)
    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert license between word and hex formats",
    )
    convert_parser.add_argument(
        "license_key",
        help="The license key to convert",
    )
    convert_parser.set_defaults(func=cmd_convert)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
