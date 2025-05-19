"""Module defining API for holiday-related operations."""

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.orm import Session

import src.holiday_group.repository as holiday_repository
from src.constants import EXC_MSG_IDS_DO_NOT_MATCH
from src.database import get_db
from src.employee.schemas import EmployeeBase
from src.holiday_group.constants import (
    BASE_URL,
    EXC_MSG_EMPLOYEES_ASSIGNED,
    EXC_MSG_HOLIDAY_GROUP_ALREADY_EXISTS,
    EXC_MSG_HOLIDAY_GROUP_NOT_FOUND,
    IDENTIFIER,
)
from src.holiday_group.schemas import HolidayGroupBase, HolidayGroupExtended
from src.services import create_event_log, requires_permission, validate

router = APIRouter(prefix=BASE_URL, tags=["holiday_group"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=HolidayGroupExtended,
)
def create_holiday_group(
    request: HolidayGroupBase,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["holiday_group.create"]
    ),
):
    """Insert new holiday group data.

    Args:
        request (HolidayGroupBase): Request data for new holiday group.
        db (Session): Database session for current request.

    Returns:
        HolidayGroupExtended: The created holiday group.

    """
    duplicate_holiday_group = holiday_repository.get_holiday_group_by_name(
        request.name, db
    )
    validate(
        duplicate_holiday_group is None,
        EXC_MSG_HOLIDAY_GROUP_ALREADY_EXISTS,
        status.HTTP_409_CONFLICT,
    )

    holiday_group = holiday_repository.create_holiday_group(request, db)
    log_args = {"holiday_group_name": holiday_group.name}
    create_event_log(IDENTIFIER, "CREATE", log_args, caller_id, db)
    return holiday_group


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[HolidayGroupExtended],
)
def get_holiday_groups(
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["holiday_group.read"]
    ),
):
    """Retrieve all holiday group data.

    Args:
        db (Session): Database session for current request.

    Returns:
        list[HolidayGroupExtended]: The retrieved holiday groups.

    """
    return holiday_repository.get_holiday_groups(db)


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=HolidayGroupExtended,
)
def get_holiday_group_by_id(
    id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["holiday_group.read"]
    ),
):
    """Retrieve data for holiday group with provided id.

    Args:
        id (int): Holiday group's unique identifier.
        db (Session): Database session for current request.

    Returns:
        HolidayGroupExtended: The retrieved holiday group.

    """
    holiday_group = holiday_repository.get_holiday_group_by_id(id, db)
    validate(
        holiday_group,
        EXC_MSG_HOLIDAY_GROUP_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    return holiday_group


@router.get(
    "/{id}/employees",
    status_code=status.HTTP_200_OK,
    response_model=list[EmployeeBase],
)
def get_employees_by_holiday_group(
    id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["holiday_group.read", "employee.read"]
    ),
):
    """Retrieve employees for holiday group with provided id.

    Args:
        id (int): Holiday group's unique identifier.
        db (Session): Database session for current request.

    Returns:
        list[EmployeeBase]: The retrieved employees.

    """
    holiday_group = holiday_repository.get_holiday_group_by_id(id, db)
    validate(
        holiday_group,
        EXC_MSG_HOLIDAY_GROUP_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    return holiday_group.employees


@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=HolidayGroupExtended,
)
def update_holiday_group_by_id(
    id: int,
    request: HolidayGroupExtended,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["holiday_group.update"]
    ),
):
    """Update data for holiday group with provided id.

    Args:
        id (int): Holiday group's unique identifier.
        request (HolidayGroupBase): Request data to update holiday group.
        db (Session): Database session for current request.

    Returns:
        HolidayGroupExtended: The updated holiday group.

    """
    validate(
        request.id == id,
        EXC_MSG_IDS_DO_NOT_MATCH,
        status.HTTP_400_BAD_REQUEST,
    )

    holiday_group = holiday_repository.get_holiday_group_by_id(id, db)
    validate(
        holiday_group,
        EXC_MSG_HOLIDAY_GROUP_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    duplicate_holiday_group = holiday_repository.get_holiday_group_by_name(
        request.name, db
    )
    validate(
        duplicate_holiday_group is None or duplicate_holiday_group.id == id,
        EXC_MSG_HOLIDAY_GROUP_ALREADY_EXISTS,
        status.HTTP_409_CONFLICT,
    )

    holiday_group = holiday_repository.update_holiday_group_by_id(
        holiday_group, request, db
    )
    log_args = {"holiday_group_name": holiday_group.name}
    create_event_log(IDENTIFIER, "UPDATE", log_args, caller_id, db)
    return holiday_group


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_holiday_group_by_id(
    id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["holiday_group.delete"]
    ),
):
    """Delete holiday group data with provided id.

    Args:
        id (int): Holiday group's unique identifier.
        db (Session): Database session for current request.

    """
    holiday_group = holiday_repository.get_holiday_group_by_id(id, db)
    validate(
        holiday_group,
        EXC_MSG_HOLIDAY_GROUP_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )
    validate(
        len(holiday_group.employees) == 0,
        EXC_MSG_EMPLOYEES_ASSIGNED,
        status.HTTP_409_CONFLICT,
    )

    holiday_repository.delete_holiday_group(holiday_group, db)
    log_args = {"holiday_group_name": holiday_group.name}
    create_event_log(IDENTIFIER, "DELETE", log_args, caller_id, db)
