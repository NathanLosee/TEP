"""Module providing the business logic for auth role-related operations."""

from typing import Optional
from fastapi import HTTPException, status
from src.auth_role.constants import (
    EXC_MSG_AUTH_ROLE_NOT_FOUND,
    EXC_MSG_NAME_ALREADY_EXISTS,
    EXC_MSG_PERMISSION_ALEADY_EXISTS,
    EXC_MSG_PERMISSION_NOT_FOUND,
    EXC_MSG_EMPLOYEE_IS_MEMBER,
    EXC_MSG_EMPLOYEE_NOT_MEMBER,
)
from src.auth_role.models import AuthRole
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
            detail=EXC_MSG_AUTH_ROLE_NOT_FOUND,
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
        bool: True if the name is unique.

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


def validate_auth_role_permission_exists(
    auth_role: AuthRole,
    permission_resource: str,
    permission_http_method: str,
    should_exist: bool,
) -> bool:
    """Return whether the provided auth role has the provided permission.

    Args:
        auth_role (AuthRole): The auth role to validate.
        permission_resource (str): The resource of the permission.
        permission_http_method (str): The HTTP method of the permission.
        should_exist (bool): Whether the permission should exist.

    Raises:
        HTTPException (404): If permission does not exist but should.
        HTTPException (409): If permission does exist but shouldn't.

    Returns:
        bool: True if the permission exists and should_exist is True,
            or if the permission does not exist and should_exist is False.

    """
    for permission in auth_role.permissions:
        if (
            permission.resource == permission_resource
            and permission.http_method == permission_http_method
        ):
            if not should_exist:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=EXC_MSG_PERMISSION_ALEADY_EXISTS,
                )
            return True
    if should_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EXC_MSG_PERMISSION_NOT_FOUND,
        )
    return True


def validate_employee_should_have_auth_role(
    auth_role: AuthRole,
    employee: Employee,
    should_exist: bool,
) -> bool:
    """Return whether the provided employee has the provided auth role.

    Args:
        auth_role (AuthRole): The auth role to validate.
        employee (Employee): The employee to validate.
        should_exist (bool): Whether the employee should have the auth role.

    Raises:
        HTTPException (404): If employee does not have auth role but should.
        HTTPException (409): If employee does have auth role but shouldn't.

    Returns:
        bool: True if the employee has the auth role and should_exist is True,
            or if the employee does not have the auth role and should_exist is
            False.

    """
    for emp in auth_role.employees:
        if employee.id == emp.id:
            if not should_exist:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=EXC_MSG_EMPLOYEE_IS_MEMBER,
                )
            return True
    if should_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EXC_MSG_EMPLOYEE_NOT_MEMBER,
        )
    return True
