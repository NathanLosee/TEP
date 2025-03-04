"""Module providing the business logic for employee-related operations."""

from fastapi import HTTPException, status
from src.employee.constants import EXC_MSG_EMPLOYEE_NOT_FOUND
from src.employee.models import Employee


def validate_employee_exists(employee: Employee | None) -> bool:
    """Return whether the provided employee exists.

    Args:
        employee (Employee): The employee to validate.
        db (Session): Database session for the current request.

    Raises:
        HTTPException (404): If employee does not exist.

    Returns:
        bool: True if employee exists.

    """
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EXC_MSG_EMPLOYEE_NOT_FOUND,
        )
    return True
