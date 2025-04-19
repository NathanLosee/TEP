"""Module providing the business logic for holiday-related operations."""

from typing import Optional
from fastapi import HTTPException, status
from src.holiday_group.constants import (
    EXC_MSG_HOLIDAY_NOT_FOUND,
    EXC_MSG_HOLIDAY_NAME_ALREADY_EXISTS,
    EXC_MSG_HOLIDAY_GROUP_NOT_FOUND,
    EXC_MSG_HOLIDAY_GROUP_ALREADY_EXISTS,
)
from src.holiday_group.models import Holiday, HolidayGroup


def validate_holiday_group_exists(holiday_group: Holiday | None) -> bool:
    """Return whether the provided holiday group exists.

    Args:
        holiday_group (Holiday): The holiday group to validate.

    Raises:
        HTTPException (404): If holiday group does not exist.

    Returns:
        bool: True if holiday group exists.

    """
    if holiday_group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EXC_MSG_HOLIDAY_GROUP_NOT_FOUND,
        )
    return True


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


def validate_holiday_group_name_is_unique(
    holiday_group_with_same_name: HolidayGroup,
    update_holiday_group_id: Optional[int],
) -> bool:
    """Return whether the provided holiday group name is unique.

    Args:
        holiday_group_with_same_name (Holiday): The holiday group that has the
            same name provided in the request.
        update_holiday_group_id (Optional[int]): Unique identifier of the
            holiday group being updated. Allows holiday group to keep same
            name.

    Raises:
        HTTPException (409): If the provided name is already in use.

    Returns:
        bool: True if holiday group name is unique.

    """
    if (
        holiday_group_with_same_name is not None
        and holiday_group_with_same_name.id != update_holiday_group_id
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=EXC_MSG_HOLIDAY_GROUP_ALREADY_EXISTS,
        )
    return True


def validate_holiday_name_is_unique_within_group(
    holiday_with_same_name: Holiday,
) -> bool:
    """Return whether the provided holiday name is unique within a group.

    Args:
        holiday_with_same_name (Holiday): The holiday that has the same name
            and group provided in the request.

    Raises:
        HTTPException (409): If the provided name is already in use.

    Returns:
        bool: True if holiday name is unique.

    """
    if holiday_with_same_name is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=EXC_MSG_HOLIDAY_NAME_ALREADY_EXISTS,
        )
    return True
