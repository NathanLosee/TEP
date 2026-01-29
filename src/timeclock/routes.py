"""Module defining API for timeclock-related operations."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Header, Security, status
from sqlalchemy.orm import Session

from src.constants import EXC_MSG_IDS_DO_NOT_MATCH
from src.database import get_db
from src.employee.constants import EXC_MSG_EMPLOYEE_NOT_FOUND
from src.employee.repository import (
    get_employee_by_badge_number as get_employee_by_badge_number_from_db,
    search_for_employees as search_for_employees_from_db,
)
from src.registered_browser.repository import get_registered_browser_by_uuid
from src.services import create_event_log, requires_license, requires_permission, validate
from src.timeclock.constants import (
    BASE_URL,
    EXC_MSG_EMPLOYEE_NOT_ALLOWED,
    EXC_MSG_EXTERNAL_CLOCK_NOT_AUTHORIZED,
    EXC_MSG_REGISTERED_BROWSER_REQUIRED,
    EXC_MSG_TIMECLOCK_ENTRY_NOT_FOUND,
    IDENTIFIER,
)
from src.timeclock.repository import (
    check_status as check_status_from_db,
    create_timeclock_entry as create_timeclock_entry_in_db,
    delete_timeclock_entry,
    get_timeclock_entries as get_timeclock_entries_from_db,
    get_timeclock_entry_by_id,
    timeclock as timeclock_in_db,
    update_timeclock_entry_by_id as update_timeclock_entry_by_id_in_db,
)
from src.timeclock.schemas import (
    TimeclockEntryBase,
    TimeclockEntryCreate,
    TimeclockEntryWithName,
)

router = APIRouter(prefix=BASE_URL, tags=["timeclock"])


@router.post(
    "/{badge_number}",
    status_code=status.HTTP_201_CREATED,
)
def timeclock(
    badge_number: str,
    db: Session = Depends(get_db),
    x_device_uuid: Optional[str] = Header(None, alias="X-Device-UUID"),
    _: None = Depends(requires_license),
):
    """Clock in/out an employee.

    Args:
        badge_number (str): Employee's badge number.
        db (Session): Database session for current request.
        x_device_uuid (Optional[str]): Device UUID header for internal devices.

    Returns:
        dict: Clock in/out status.

    """
    employee = get_employee_by_badge_number_from_db(badge_number, db)
    validate(
        employee,
        EXC_MSG_EMPLOYEE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )
    validate(
        employee.allow_clocking,
        EXC_MSG_EMPLOYEE_NOT_ALLOWED,
        status.HTTP_403_FORBIDDEN,
    )

    # Check if browser UUID is provided (browser has saved UUID)
    if x_device_uuid:
        # Check if browser is registered in system
        browser = get_registered_browser_by_uuid(x_device_uuid, db)

        if browser:
            # Registered company browser - anyone can use it
            pass
        else:
            # Unregistered browser - only employees with external_clock_allowed can use
            validate(
                employee.external_clock_allowed,
                EXC_MSG_EXTERNAL_CLOCK_NOT_AUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            )
    else:
        # No browser UUID - only employees with external_clock_allowed can clock
        validate(
            employee.external_clock_allowed,
            EXC_MSG_REGISTERED_BROWSER_REQUIRED,
            status.HTTP_403_FORBIDDEN,
        )

    log_args = {"badge_number": employee.badge_number}
    if x_device_uuid:
        log_args["device_uuid"] = x_device_uuid

    if timeclock_in_db(badge_number, db):
        create_event_log(IDENTIFIER, "CLOCK_IN", log_args, "0", db)
        return {"status": "success", "message": "Clocked in"}
    else:
        create_event_log(IDENTIFIER, "CLOCK_OUT", log_args, "0", db)
        return {"status": "success", "message": "Clocked out"}


@router.get(
    "/{badge_number}/status",
    status_code=status.HTTP_200_OK,
)
def check_status(
    badge_number: str,
    db: Session = Depends(get_db),
):
    """Check the clock status of an employee.

    Args:
        badge_number (str): Employee's badge number.
        db (Session): Database session for current request.

    Returns:
        dict: Clock in/out status.

    """
    employees = search_for_employees_from_db(badge_number=badge_number, db=db)
    validate(
        len(employees) == 1 and employees[0].allow_clocking,
        EXC_MSG_EMPLOYEE_NOT_ALLOWED,
        status.HTTP_403_FORBIDDEN,
    )

    if check_status_from_db(badge_number, db):
        return {"status": "success", "message": "Clocked in"}
    else:
        return {"status": "success", "message": "Clocked out"}


@router.get(
    "/{badge_number}/history",
    status_code=status.HTTP_200_OK,
    response_model=list[TimeclockEntryWithName],
)
def get_employee_history(
    badge_number: str,
    start_timestamp: datetime,
    end_timestamp: datetime,
    db: Session = Depends(get_db),
):
    """Retrieve timeclock history for a specific employee.
    This endpoint does not require special permissions - employees can view their own history.

    Args:
        badge_number (str): Employee's badge number.
        start_timestamp (datetime): Start timestamp for the time period.
        end_timestamp (datetime): End timestamp for the time period.
        db (Session): Database session for current request.

    Returns:
        list[TimeclockEntryWithName]: The retrieved timeclock entries.

    """
    employees = search_for_employees_from_db(badge_number=badge_number, db=db)
    validate(
        len(employees) == 1 and employees[0].allow_clocking,
        EXC_MSG_EMPLOYEE_NOT_ALLOWED,
        status.HTTP_403_FORBIDDEN,
    )

    return get_timeclock_entries_from_db(
        start_timestamp, end_timestamp, badge_number, None, None, db
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=TimeclockEntryBase,
)
def create_manual_timeclock_entry(
    request: TimeclockEntryCreate,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["timeclock.create"]
    ),
    _: None = Depends(requires_license),
):
    """Create a manual timeclock entry.

    Args:
        request (TimeclockEntryCreate): Request data to create timeclock entry.
        db (Session): Database session for current request.

    Returns:
        TimeclockEntryBase: The created timeclock entry.

    """
    # Validate employee exists
    employee = get_employee_by_badge_number_from_db(request.badge_number, db)
    validate(
        employee,
        EXC_MSG_EMPLOYEE_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    timeclock_entry = create_timeclock_entry_in_db(request, db)
    log_args = {"timeclock_entry_id": timeclock_entry.id}
    create_event_log(IDENTIFIER, "MANUAL_CREATE", log_args, caller_badge, db)
    return timeclock_entry


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[TimeclockEntryWithName],
)
def get_timeclock_entries(
    start_timestamp: datetime,
    end_timestamp: datetime,
    badge_number: str = None,
    first_name: str = None,
    last_name: str = None,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["timeclock.read"]
    ),
):
    """Retrieve all timeclock entries with given time period.
    If badge_number is provided, it will be used to filter the entries to
        those associated with the badge_number.

    Args:
        start_timestamp (datetime): Start timestamp for the time period.
        end_timestamp (datetime): End timestamp for the time period.
        badge_number (str, optional): Employee's badge number.
            Defaults to None.
        first_name (str, optional): Employee's first name to filter by.
            Defaults to None.
        last_name (str, optional): Employee's last name to filter by.
            Defaults to None.
        db (Session): Database session for current request.

    Returns:
        list[TimeclockEntryBase]: The retrieved timeclock entries.

    """
    return get_timeclock_entries_from_db(
        start_timestamp, end_timestamp, badge_number, first_name, last_name, db
    )


@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=TimeclockEntryBase,
)
def update_timeclock_by_id(
    id: int,
    request: TimeclockEntryBase,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["timeclock.update"]
    ),
    _: None = Depends(requires_license),
):
    """Update data for timeclock entry with provided id.

    Args:
        id (int): Timeclock entry's unique identifier.
        request (TimeclockGroupBase): Request data to update timeclock entry.
        db (Session): Database session for current request.

    Returns:
        TimeclockEntryBase: The updated timeclock entry.

    """
    validate(
        request.id == id,
        EXC_MSG_IDS_DO_NOT_MATCH,
        status.HTTP_400_BAD_REQUEST,
    )

    timeclock = get_timeclock_entry_by_id(id, db)
    validate(
        timeclock,
        EXC_MSG_TIMECLOCK_ENTRY_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    timeclock_entry = update_timeclock_entry_by_id_in_db(timeclock, request, db)
    log_args = {"timeclock_entry_id": timeclock_entry.id}
    create_event_log(IDENTIFIER, "UPDATE", log_args, caller_badge, db)
    return timeclock_entry


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_timeclock_by_id(
    id: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["timeclock.delete"]
    ),
    _: None = Depends(requires_license),
):
    """Delete timeclock data with provided id.

    Args:
        id (int): Timeclock entry's unique identifier.
        db (Session): Database session for current request.

    """
    timeclock_entry = get_timeclock_entry_by_id(id, db)
    validate(
        timeclock_entry,
        EXC_MSG_TIMECLOCK_ENTRY_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    delete_timeclock_entry(timeclock_entry, db)
    log_args = {"timeclock_entry_id": timeclock_entry.id}
    create_event_log(IDENTIFIER, "DELETE", log_args, caller_badge, db)
