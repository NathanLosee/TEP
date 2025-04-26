"""Module for defining global-level constants."""

import enum


DIGIT_REGEX = "[[:digit:]]"
CAP_CHAR_REGEX = "[[:upper:]]"
NAME_CHAR_REGEX = "[-'' [:alpha:]]"
EXC_MSG_IDS_DO_NOT_MATCH = "Ids in body and path do not match."


class HTTPMethod(enum.Enum):
    """Class to define HTTP methods."""

    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class ResourceType(enum.Enum):
    """Class to define resource types."""

    EMPLOYEE = "EMPLOYEE"
    DEPARTMENT = "DEPARTMENT"
    DEPARTMENT_MEMBERSHIP = "DEPARTMENT_MEMBERSHIP"
    HOLIDAY = "HOLIDAY"
    ORG_UNIT = "ORG_UNIT"
    AUTH_ROLE = "AUTH_ROLE"
    AUTH_ROLE_PERMISSION = "AUTH_ROLE_PERMISSION"
    AUTH_ROLE_MEMBERSHIP = "AUTH_ROLE_MEMBERSHIP"
