"""Module for defining auth-level constants."""

from src.constants import NAME_CHAR_REGEX as N

IDENTIFIER = "auth_roles"
MEMBERSHIP_IDENTIFIER = "auth_role_memberships"
BASE_URL = f"/{IDENTIFIER}"
NAME_REGEX = f"^{N}+$"
NAME_MAX_LENGTH = 100
EXC_MSG_NAME_ALREADY_EXISTS = "Auth with name already exists."
EXC_MSG_AUTH_NOT_FOUND = "Auth does not exist."
EXC_MSG_EMPLOYEE_IS_MEMBER = "The employee already has this auth."
EXC_MSG_EMPLOYEE_NOT_MEMBER = "The employee does not have this auth."
