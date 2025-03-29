"""Module for defining global-level constants."""

import enum


DIGIT_REGEX = "[[:digit:]]"
CAP_CHAR_REGEX = "[[:upper:]]"
NAME_CHAR_REGEX = "[-''[:alpha:]]"
EXC_MSG_IDS_DO_NOT_MATCH = "Ids in body and path do not match."


class HTTPMethod(enum.Enum):
    """Class to define HTTP methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class ResourceType(enum.Enum):
    """Class to define resource types."""

    EMPLOYEE = "employee"
    DEPARTMENT = "department"
    HOLIDAY = "holiday"
    JOB = "job"
    ORG_UNIT = "org_unit"
    AUTH_ROLE = "auth_role"
    AUTH_ROLE_PERMISSION = "auth_role_permission"
    AUTH_ROLE_MEMBERSHIP = "auth_role_membership"
