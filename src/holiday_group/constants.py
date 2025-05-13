"""Module for defining holiday-level constants."""

from src.constants import NAME_CHAR_REGEX as N

IDENTIFIER = "holiday_groups"
HOLIDAY_IDENTIFIER = "holidays"
BASE_URL = f"/{IDENTIFIER}"
NAME_REGEX = f"^{N}+$"
NAME_MAX_LENGTH = 100
EXC_MSG_END_DATE_BEFORE_START_DATE = (
    "end_date must be greater than or equal to start_date."
)
EXC_MSG_DUPLICATE_HOLIDAY_NAME = "Duplicate holiday name found."
EXC_MSG_HOLIDAY_GROUP_NOT_FOUND = "Holiday group does not exist."
EXC_MSG_HOLIDAY_GROUP_ALREADY_EXISTS = (
    "Holiday group with name already exists within this group."
)
