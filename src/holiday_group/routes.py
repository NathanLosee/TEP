"""Module defining API for holiday-related operations."""

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.orm import Session

from src.constants import EXC_MSG_IDS_DO_NOT_MATCH
from src.database import get_db
from src.employee.schemas import EmployeeExtended
from src.holiday_group.constants import (
    BASE_URL,
    EXC_MSG_EMPLOYEES_ASSIGNED,
    EXC_MSG_HOLIDAY_GROUP_ALREADY_EXISTS,
    EXC_MSG_HOLIDAY_GROUP_NOT_FOUND,
    IDENTIFIER,
)
from src.holiday_group.repository import (
    create_holiday_group as create_holiday_group_in_db,
    delete_holiday_group as delete_holiday_group_from_db,
    get_holiday_group_by_id as get_holiday_group_by_id_from_db,
    get_holiday_group_by_name,
    get_holiday_groups as get_holiday_groups_from_db,
    update_holiday_group_by_id as update_holiday_group_by_id_in_db,
)
from src.holiday_group.schemas import HolidayGroupBase, HolidayGroupExtended
from src.holiday_group.utils import get_holidays_for_year
from src.services import create_event_log, requires_license, requires_permission, validate

router = APIRouter(prefix=BASE_URL, tags=["holiday_group"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=HolidayGroupExtended,
)
def create_holiday_group(
    request: HolidayGroupBase,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
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
    duplicate_holiday_group = get_holiday_group_by_name(request.name, db)
    validate(
        duplicate_holiday_group is None,
        EXC_MSG_HOLIDAY_GROUP_ALREADY_EXISTS,
        status.HTTP_409_CONFLICT,
    )

    holiday_group = create_holiday_group_in_db(request, db)
    log_args = {"holiday_group_name": holiday_group.name}
    create_event_log(IDENTIFIER, "CREATE", log_args, caller_badge, db)
    return holiday_group


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[HolidayGroupExtended],
)
def get_holiday_groups(
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["holiday_group.read"]
    ),
):
    """Retrieve all holiday group data.

    Args:
        db (Session): Database session for current request.

    Returns:
        list[HolidayGroupExtended]: The retrieved holiday groups.

    """
    return get_holiday_groups_from_db(db)


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=HolidayGroupExtended,
)
def get_holiday_group(
    id: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
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
    holiday_group = get_holiday_group_by_id_from_db(id, db)
    validate(
        holiday_group,
        EXC_MSG_HOLIDAY_GROUP_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    return holiday_group


@router.get(
    "/{id}/employees",
    status_code=status.HTTP_200_OK,
    response_model=list[EmployeeExtended],
)
def get_employees_by_holiday_group(
    id: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["holiday_group.read", "employee.read"]
    ),
):
    """Retrieve employees for holiday group with provided id.

    Args:
        id (int): Holiday group's unique identifier.
        db (Session): Database session for current request.

    Returns:
        list[EmployeeExtended]: The retrieved employees.

    """
    holiday_group = get_holiday_group_by_id_from_db(id, db)
    validate(
        holiday_group,
        EXC_MSG_HOLIDAY_GROUP_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    return holiday_group.employees


@router.get(
    "/{id}/year/{year}",
    status_code=status.HTTP_200_OK,
)
def get_holidays_for_year_by_group(
    id: int,
    year: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["holiday_group.read"]
    ),
):
    """Generate holiday instances for a specific year.

    Args:
        id (int): Holiday group's unique identifier.
        year (int): Year to generate holidays for.
        db (Session): Database session for current request.

    Returns:
        list[dict]: List of holiday instances with name, start_date, end_date.

    """
    holiday_group = get_holiday_group_by_id_from_db(id, db)
    validate(
        holiday_group,
        EXC_MSG_HOLIDAY_GROUP_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    return get_holidays_for_year(holiday_group.holidays, year)


@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=HolidayGroupExtended,
)
def update_holiday_group(
    id: int,
    request: HolidayGroupExtended,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
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

    holiday_group = get_holiday_group_by_id_from_db(id, db)
    validate(
        holiday_group,
        EXC_MSG_HOLIDAY_GROUP_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    duplicate_holiday_group = get_holiday_group_by_name(request.name, db)
    validate(
        duplicate_holiday_group is None or duplicate_holiday_group.id == id,
        EXC_MSG_HOLIDAY_GROUP_ALREADY_EXISTS,
        status.HTTP_409_CONFLICT,
    )

    holiday_group = update_holiday_group_by_id_in_db(holiday_group, request, db)
    log_args = {"holiday_group_name": holiday_group.name}
    create_event_log(IDENTIFIER, "UPDATE", log_args, caller_badge, db)
    return holiday_group


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_holiday_group(
    id: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["holiday_group.delete"]
    ),
):
    """Delete holiday group data with provided id.

    Args:
        id (int): Holiday group's unique identifier.
        db (Session): Database session for current request.

    """
    holiday_group = get_holiday_group_by_id_from_db(id, db)
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

    delete_holiday_group_from_db(holiday_group, db)
    log_args = {"holiday_group_name": holiday_group.name}
    create_event_log(IDENTIFIER, "DELETE", log_args, caller_badge, db)
