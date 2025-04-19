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
    """Validate user credentials.

    Args:
        employee (Employee): The employee object containing user credentials.

    Returns:
        bool: True if credentials are valid, False otherwise.

    """
    if employee:
        return True
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=EXC_MSG_LOGIN_FAILED,
        )


def generate_permission_list(employee: Employee) -> list[dict]:
    """Generate permission list for the logged-in user.

    Args:
        employee (Employee): The employee object containing user credentials.

    Returns:
        list[dict]: A list of unique permissions for the user.

    """
    permissions_set = set()
    for auth_role in employee.auth_roles:
        for permission in auth_role.permissions:
            if not permission.restrict_to_self:
                permissions_set.discard(
                    (
                        permission.resource,
                        permission.http_method,
                        True,
                    )
                )
            permissions_set.add(
                (
                    permission.resource,
                    permission.http_method,
                    permission.restrict_to_self,
                )
            )
    return [
        {
            "resource": resource,
            "http_method": http_method,
            "restrict_to_self": restrict_to_self,
        }
        for resource, http_method, restrict_to_self, _ in permissions_set
    ]
