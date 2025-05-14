"""Module providing the business logic for timeclock-related operations."""

from fastapi import HTTPException, status
from src.timeclock.constants import (
    EXC_MSG_EMPLOYEE_NOT_ALLOWED,
    EXC_MSG_TIMECLOCK_ENTRY_NOT_FOUND,
)
from src.timeclock.models import TimeclockEntry


def validate_timeclock_entry_exists(
    timeclock_entry: TimeclockEntry | None,
) -> bool:
    """Validates whether a timeclock entry exists.

    Args:
        timeclock_entry (TimeclockEntry | None): The timeclock entry to
            validate.

    Raises:
        HTTPException (404): If the timeclock entry does not exist.

    Returns:
        bool: True if the timeclock entry exists.

    """
    if not timeclock_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EXC_MSG_TIMECLOCK_ENTRY_NOT_FOUND,
        )
    return True


def validate_employee_allowed(allow_clocking: bool) -> bool:
    """Validates whether employee is allowed to clock in/out.

    Args:
        allow_clocking (bool): Indicates if the employee is allowed to clock
            in/out.

    Raises:
        HTTPException (403): If the employee is not allowed to clock in/out.

    Returns:
        bool: True if the employee is allowed to clock in/out, False otherwise.

    """
    if not allow_clocking:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=EXC_MSG_EMPLOYEE_NOT_ALLOWED,
        )
    return True
