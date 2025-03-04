"""Module providing the business logic for department-related operations."""

from typing import Optional
from fastapi import HTTPException, status
from src.department.constants import (
    EXC_MSG_DEPARTMENT_NOT_FOUND,
    EXC_MSG_NAME_ALREADY_EXISTS,
    EXC_MSG_EMPLOYEE_IS_MEMBER,
    EXC_MSG_EMPLOYEE_NOT_MEMBER,
    EXC_MSG_EMPLOYEES_ASSIGNED,
    EXC_MSG_JOBS_ASSIGNED,
)
from src.department.models import Department
from src.employee.models import Employee


def validate_department_exists(department: Department | None) -> bool:
    """Return whether the provided department exists.

    Args:
        department (Department): The department to validate.

    Raises:
        HTTPException (404): If department does not exist.

    Returns:
        bool: True if department exists.

    """
    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EXC_MSG_DEPARTMENT_NOT_FOUND,
        )
    return True


def validate_department_name_is_unique(
    department_with_same_name: Department, update_department_id: Optional[int]
) -> bool:
    """Return whether the provided department name is unique.

    Args:
        department_with_same_name (Department): The department that has the
            same name provided in the request.
        update_department_id (Optional[int]): Unique identifier of the
            department being updated. Allows department to keep same name.

    Raises:
        HTTPException (409): If the provided name is already in use.

    Returns:
        bool: True if department name is unique.

    """
    if (
        department_with_same_name is not None
        and department_with_same_name.id != update_department_id
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=EXC_MSG_NAME_ALREADY_EXISTS,
        )
    return True


def validate_employee_is_in_department(
    department: Department,
    employee: Employee,
) -> bool:
    """Return whether the provided department has the provided employee.

    Args:
        department (Department): The department to validate.
        employee (Employee): The employee to validate.

    Raises:
        HTTPException (409): If department does not have employee.

    Returns:
        bool: True if department does have employee.

    """
    for emp in department.employees:
        if employee.id == emp.id:
            return True
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=EXC_MSG_EMPLOYEE_NOT_MEMBER,
    )


def validate_employee_is_not_in_department(
    department: Department,
    employee: Employee,
) -> bool:
    """Return whether the provided department has the provided employee.

    Args:
        department (Department): The department to validate.
        employee (Employee): The employee to validate.

    Raises:
        HTTPException (409): If department does have employee.

    Returns:
        bool: True if department does not have employee.

    """
    for emp in department.employees:
        if employee.id == emp.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=EXC_MSG_EMPLOYEE_IS_MEMBER,
            )
    return True


def validate_department_employees_list_is_empty(
    department: Department | None,
) -> bool:
    """Return whether the provided department has employees.

    Args:
        department (Department): The department to validate.

    Raises:
        HTTPException (409): If department does have employees.

    Returns:
        bool: True if department does not have employees.

    """
    if department.employees is not None and len(department.employees) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=EXC_MSG_EMPLOYEES_ASSIGNED,
        )
    return True


def validate_department_jobs_list_is_empty(
    department: Department | None,
) -> bool:
    """Return whether the provided department has jobs.

    Args:
        department (Department): The department to validate.

    Raises:
        HTTPException (409): If department does have jobs.

    Returns:
        bool: True if department does not have jobs.

    """
    if department.jobs is not None and len(department.jobs) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=EXC_MSG_JOBS_ASSIGNED,
        )
    return True
