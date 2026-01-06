"""Module defining API for timeclock-related operations."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Header, Security, status
from sqlalchemy.orm import Session

import src.employee.routes as employee_routes
import src.registered_browser.repository as browser_repository
import src.timeclock.repository as timeclock_repository
from src.constants import EXC_MSG_IDS_DO_NOT_MATCH
from src.database import get_db
from src.services import create_event_log, requires_permission, validate
from src.timeclock.constants import (
    BASE_URL,
    EXC_MSG_EMPLOYEE_NOT_ALLOWED,
    EXC_MSG_TIMECLOCK_ENTRY_NOT_FOUND,
    IDENTIFIER,
)
from src.timeclock.schemas import TimeclockEntryBase, TimeclockEntryWithName

router = APIRouter(prefix=BASE_URL, tags=["timeclock"])


@router.post(
    "/{badge_number}",
    status_code=status.HTTP_201_CREATED,
)
def timeclock(
    badge_number: str,
    db: Session = Depends(get_db),
    x_device_uuid: Optional[str] = Header(None, alias="X-Device-UUID"),
):
    """Clock in/out an employee.

    Args:
        badge_number (str): Employee's badge number.
        db (Session): Database session for current request.
        x_device_uuid (Optional[str]): Device UUID header for internal devices.

    Returns:
        dict: Clock in/out status.

    """
    employee = employee_routes.get_employee_by_badge_number(badge_number, db)
    validate(
        employee.allow_clocking,
        EXC_MSG_EMPLOYEE_NOT_ALLOWED,
        status.HTTP_403_FORBIDDEN,
    )

    # Check if browser UUID is provided (browser has saved UUID)
    if x_device_uuid:
        # Check if browser is registered in system
        browser = browser_repository.get_registered_browser_by_uuid(
            x_device_uuid, db
        )

        if browser:
            # Registered company browser - anyone can use it
            pass
        else:
            # Unregistered browser - only employees with external_clock_allowed can use
            validate(
                employee.external_clock_allowed,
                "Employee is not authorized to clock from unregistered browsers",
                status.HTTP_403_FORBIDDEN,
            )
    else:
        # No browser UUID - only employees with external_clock_allowed can clock
        validate(
            employee.external_clock_allowed,
            "Employee must clock from a registered company browser",
            status.HTTP_403_FORBIDDEN,
        )

    log_args = {"badge_number": employee.badge_number}
    if x_device_uuid:
        log_args["device_uuid"] = x_device_uuid

    if timeclock_repository.timeclock(badge_number, db):
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
    x_device_uuid: Optional[str] = Header(None, alias="X-Device-UUID"),
):
    """Check the clock status of an employee.

    Args:
        badge_number (str): Employee's badge number.
        db (Session): Database session for current request.
        x_device_uuid (Optional[str]): Device UUID header for external devices.

    Returns:
        dict: Clock in/out status.

    """
    employees = employee_routes.search_for_employees(
        badge_number=badge_number, db=db
    )
    validate(
        len(employees) == 1 and employees[0].allow_clocking,
        EXC_MSG_EMPLOYEE_NOT_ALLOWED,
        status.HTTP_403_FORBIDDEN,
    )

    employee = employees[0]

    # Check if browser UUID is provided (browser has saved UUID)
    if x_device_uuid:
        # Check if browser is registered in system
        browser = browser_repository.get_registered_browser_by_uuid(
            x_device_uuid, db
        )

        if browser:
            # Registered company browser - anyone can use it
            pass
        else:
            # Unregistered browser - only employees with external_clock_allowed can use
            validate(
                employee.external_clock_allowed,
                "Employee is not authorized to clock from unregistered browsers",
                status.HTTP_403_FORBIDDEN,
            )
    else:
        # No browser UUID - only employees with external_clock_allowed can clock
        validate(
            employee.external_clock_allowed,
            "Employee must clock from a registered company browser",
            status.HTTP_403_FORBIDDEN,
        )

    if timeclock_repository.check_status(badge_number, db):
        return {"status": "success", "message": "Clocked in"}
    else:
        return {"status": "success", "message": "Clocked out"}


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
    return timeclock_repository.get_timeclock_entries(
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

    timeclock = timeclock_repository.get_timeclock_entry_by_id(id, db)
    validate(
        timeclock,
        EXC_MSG_TIMECLOCK_ENTRY_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    timeclock_entry = timeclock_repository.update_timeclock_entry_by_id(
        timeclock, request, db
    )
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
):
    """Delete timeclock data with provided id.

    Args:
        id (int): Timeclock entry's unique identifier.
        db (Session): Database session for current request.

    """
    timeclock_entry = timeclock_repository.get_timeclock_entry_by_id(id, db)
    validate(
        timeclock_entry,
        EXC_MSG_TIMECLOCK_ENTRY_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    timeclock_repository.delete_timeclock_entry(timeclock_entry, db)
    log_args = {"timeclock_entry_id": timeclock_entry.id}
    create_event_log(IDENTIFIER, "DELETE", log_args, caller_badge, db)
