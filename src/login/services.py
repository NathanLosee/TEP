"""Module providing the business logic for login-related operations."""

from typing import Optional
from fastapi import HTTPException, status
from src.employee.models import Employee
from src.login.constants import (
    EXC_MSG_LOGIN_FAILED,
)


def validate_login(
    employee: Employee,
) -> Optional[bool]:
    """
    Validate user credentials.

    Args:
        employee (Employee): The employee object containing user credentials.

    Returns:
        bool: True if credentials are valid, False otherwise.
    """
    # Placeholder for actual authentication logic
    if employee:
        return True
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=EXC_MSG_LOGIN_FAILED,
        )


def generate_permissions(
    employee: Employee,
) -> dict[str, list[dict[str, str]]]:
    """
    Generate permissions for the authenticated user.

    Args:
        employee (Employee): The employee object containing user credentials.

    Returns:
        dict[str, list[dict[str, str]]]: A dictionary of permissions for the
            user.
    """
    permissions = {}
    resources = set()
    for permission in employee.auth_role.permissions:
        resources.add(permission.resource)
    for resource in resources:
        permissions[resource] = {
            [
                {
                    "http_method": permission.http_method,
                    "restrict_to_self": permission.restrict_to_self,
                }
                for permission in employee.auth_role.permissions
                if permission.resource == permission.resource
            ]
        }
    return permissions
