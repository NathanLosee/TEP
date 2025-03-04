"""Module providing the business logic for holiday-related operations."""

from typing import Optional
from fastapi import HTTPException, status
from src.holiday.constants import (
    EXC_MSG_HOLIDAY_NOT_FOUND,
    EXC_MSG_NAME_ALREADY_EXISTS,
)
from src.holiday.models import Holiday


def validate_holiday_exists(holiday: Holiday | None) -> bool:
    """Return whether the provided holiday exists.

    Args:
        holiday (Holiday): The holiday to validate.
        db (Session): Database session for the current request.

    Raises:
        HTTPException (404): If holiday does not exist.

    Returns:
        bool: True if holiday exists.

    """
    if holiday is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EXC_MSG_HOLIDAY_NOT_FOUND,
        )
    return True


def validate_holiday_name_is_unique_within_org_unit(
    holiday_with_same_name: Holiday, update_holiday_id: Optional[int]
) -> bool:
    """Return whether the provided holiday name is unique within a org unit.

    Args:
        holiday_with_same_name (Holiday): The holiday that has the same name
            and org unit provided in the request.
        update_holiday_id (Optional[int]): Unique identifier of the holiday
            being updated. Allows holiday to keep same name.

    Raises:
        HTTPException (409): If the provided name is already in use.

    Returns:
        bool: True if holiday name is unique.

    """
    if (
        holiday_with_same_name is not None
        and holiday_with_same_name.id != update_holiday_id
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=EXC_MSG_NAME_ALREADY_EXISTS,
        )
    return True
