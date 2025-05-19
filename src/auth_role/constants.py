"""Module for defining auth role-level constants."""

from src.constants import NAME_CHAR_REGEX as N

IDENTIFIER = "auth_roles"
MEMBERSHIP_IDENTIFIER = "auth_role_memberships"
PERMISSION_IDENTIFIER = "auth_role_permissions"
BASE_URL = f"/{IDENTIFIER}"
NAME_REGEX = f"^{N}+$"
NAME_MAX_LENGTH = 100
EXC_MSG_INVALID_RESOURCE = "An invalid resource permission was found."
EXC_MSG_NAME_ALREADY_EXISTS = "Auth role with name already exists."
EXC_MSG_AUTH_ROLE_NOT_FOUND = "Auth role does not exist."
EXC_MSG_USER_IS_MEMBER = "The user already has this auth role."
EXC_MSG_USER_NOT_MEMBER = "The user does not have this auth role."
EXC_MSG_USERS_ASSIGNED = "Users are assigned this auth role."
