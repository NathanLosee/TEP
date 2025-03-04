"""Module providing the business logic for auth role-related operations."""

from typing import Optional
from fastapi import HTTPException, status
from src.auth.constants import (
    EXC_MSG_AUTH_NOT_FOUND,
    EXC_MSG_NAME_ALREADY_EXISTS,
    EXC_MSG_EMPLOYEE_IS_MEMBER,
    EXC_MSG_EMPLOYEE_NOT_MEMBER,
)
from src.auth.models import AuthRole
from src.employee.models import Employee


def validate_auth_role_exists(auth_role: AuthRole | None) -> bool:
    """Return whether the provided auth role exists.

    Args:
        auth_role (AuthRole): The auth role to validate.

    Raises:
        HTTPException (404): If auth role does not exist.

    Returns:
        bool: True if auth role exists.

    """
    if auth_role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EXC_MSG_AUTH_NOT_FOUND,
        )
    return True


def validate_auth_role_name_is_unique(
    auth_role_with_same_name: AuthRole, update_auth_role_id: Optional[int]
) -> bool:
    """Return whether the provided auth role name is unique.

    Args:
        auth_role_with_same_name (AuthRole): The auth role that has the
            same name provided in the request.
        update_auth_role_id (Optional[int]): Unique identifier of the
            auth_role being updated. Allows auth role to keep same name.

    Raises:
        HTTPException (409): If the provided name is already in use.

    Returns:
        bool: True if auth role name is unique.

    """
    if (
        auth_role_with_same_name is not None
        and auth_role_with_same_name.id != update_auth_role_id
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=EXC_MSG_NAME_ALREADY_EXISTS,
        )
    return True


def validate_employee_is_in_auth_role(
    auth_role: AuthRole,
    employee: Employee,
) -> bool:
    """Return whether the provided auth role has the provided employee.

    Args:
        auth_role (AuthRole): The auth role to validate.
        employee (Employee): The employee to validate.

    Raises:
        HTTPException (409): If employee does not have auth role.

    Returns:
        bool: True if auth role does have employee.

    """
    for emp in auth_role.employees:
        if employee.id == emp.id:
            return True
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=EXC_MSG_EMPLOYEE_NOT_MEMBER,
    )


def validate_employee_is_not_in_auth_role(
    auth_role: AuthRole,
    employee: Employee,
) -> bool:
    """Return whether the provided auth role has the provided employee.

    Args:
        auth_role (AuthRole): The auth role to validate.
        employee (Employee): The employee to validate.

    Raises:
        HTTPException (409): If employee does have auth role.

    Returns:
        bool: True if auth role does not have employee.

    """
    for emp in auth_role.employees:
        if employee.id == emp.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=EXC_MSG_EMPLOYEE_IS_MEMBER,
            )
    return True
