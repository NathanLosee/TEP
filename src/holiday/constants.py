"""Module for defining holiday-level constants."""

from src.constants import NAME_CHAR_REGEX as N

IDENTIFIER = "holidays"
BASE_URL = f"/{IDENTIFIER}"
NAME_REGEX = f"^{N}+$"
NAME_MAX_LENGTH = 100
EXC_MSG_NAME_ALREADY_EXISTS = (
    "Holiday with name already exists within this org unit."
)
EXC_MSG_HOLIDAY_NOT_FOUND = "Holiday does not exist."
EXC_MSG_DATE_ALREADY_EXISTS = "Holiday with date already exists."
