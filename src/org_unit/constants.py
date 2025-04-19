"""Module for defining org unit-level constants."""

from src.constants import NAME_CHAR_REGEX as N

IDENTIFIER = "org_units"
BASE_URL = f"/{IDENTIFIER}"
NAME_REGEX = f"^{N}+$"
NAME_MAX_LENGTH = 100
EXC_MSG_ORG_NOT_FOUND = "Org unit does not exist."
EXC_MSG_NAME_ALREADY_EXISTS = "Org unit with name already exists."
EXC_MSG_EMPLOYEES_ASSIGNED = "Employees are assigned to this org unit."
