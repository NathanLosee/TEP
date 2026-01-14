"""Module for generating human-readable device UUIDs.

The UUIDs are in the format: WORD1-WORD2-WORD3-NUMBER
Example: EAGLE-RIVER-MOUNTAIN-42

This makes them easy to type and remember while maintaining uniqueness.
"""

import random
from pathlib import Path
from typing import Set


def _load_word_list() -> list[str]:
    """Load word list from words.txt file.

    Returns:
        list[str]: List of uppercase words
    """
    words_file = Path(__file__).parent.parent.parent / "words.txt"
    with open(words_file, "r", encoding="utf-8") as f:
        return [line.strip().upper() for line in f if line.strip()]


# Load word list from external file
WORD_LIST = _load_word_list()


def generate_readable_uuid() -> str:
    """Generate a human-readable UUID in format WORD1-WORD2-WORD3-NUMBER.

    Returns:
        str: A unique identifier like "EAGLE-RIVER-MOUNTAIN-42"
    """
    # Select 3 random words
    words = random.sample(WORD_LIST, 3)

    # Generate a random number between 10 and 99
    number = random.randint(10, 99)

    # Combine into UUID format
    return f"{words[0]}-{words[1]}-{words[2]}-{number}"


def validate_uuid_format(uuid: str) -> bool:
    """Validate that a UUID matches the expected format.

    Args:
        uuid: The UUID string to validate

    Returns:
        bool: True if the UUID matches the format WORD-WORD-WORD-NUMBER
    """
    parts = uuid.split("-")

    # Must have exactly 4 parts
    if len(parts) != 4:
        return False

    # First 3 parts must be uppercase letters
    for i in range(3):
        if not parts[i].isupper() or not parts[i].isalpha():
            return False

    # Last part must be a number
    if not parts[3].isdigit():
        return False

    return True


def is_uuid_unique(uuid: str, existing_uuids: Set[str]) -> bool:
    """Check if a UUID is unique against a set of existing UUIDs.

    Args:
        uuid: The UUID to check
        existing_uuids: Set of existing UUIDs to check against

    Returns:
        bool: True if the UUID is unique
    """
    return uuid not in existing_uuids


def generate_unique_uuid(existing_uuids: Set[str], max_attempts: int = 100) -> str:
    """Generate a unique UUID that doesn't exist in the provided set.

    Args:
        existing_uuids: Set of UUIDs that already exist
        max_attempts: Maximum number of generation attempts before giving up

    Returns:
        str: A unique UUID

    Raises:
        RuntimeError: If unable to generate unique UUID after max_attempts
    """
    for _ in range(max_attempts):
        uuid = generate_readable_uuid()
        if is_uuid_unique(uuid, existing_uuids):
            return uuid

    raise RuntimeError(
        f"Failed to generate unique UUID after {max_attempts} attempts. "
        "This is extremely unlikely and may indicate a problem with the word list."
    )
