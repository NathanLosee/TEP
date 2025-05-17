"""Module defining API for timeclock-related operations."""

from datetime import datetime
from fastapi import APIRouter, Security, status, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.login.services import requires_permission
import src.services as common_services
from src.timeclock.constants import BASE_URL, IDENTIFIER
import src.timeclock.repository as timeclock_repository
import src.timeclock.services as timeclock_services
from src.timeclock.schemas import TimeclockEntryBase
import src.employee.routes as employee_routes
from src.event_log.constants import EVENT_LOG_MSGS
import src.event_log.routes as event_log_routes
from src.event_log.schemas import EventLogBase

router = APIRouter(prefix=BASE_URL, tags=["timeclock"])


@router.post(
    "/{id}",
    status_code=status.HTTP_201_CREATED,
)
def timeclock(id: int, db: Session = Depends(get_db)):
    """Clock in/out an employee.

    Args:
        id (int): The employee's unique identifier.
        db (Session): Database session for current request.

    Returns:
        dict: Json response with clock in/out status.

    """
    employee = employee_routes.get_employee_by_id(id, db)
    timeclock_services.validate_employee_allowed(employee.allow_clocking)

    if timeclock_repository.timeclock(id, db):
        event_log_routes.create_event_log(
            EventLogBase(
                log=EVENT_LOG_MSGS[IDENTIFIER]["CLOCK_IN"].format(
                    employee_id=employee.id
                ),
                employee_id=employee.id,
            ),
            db,
        )
        return {"status": "success", "message": "Clocked in"}
    else:
        event_log_routes.create_event_log(
            EventLogBase(
                log=EVENT_LOG_MSGS[IDENTIFIER]["CLOCK_OUT"].format(
                    employee_id=employee.id
                ),
                employee_id=employee.id,
            ),
            db,
        )
        return {"status": "success", "message": "Clocked out"}


@router.get(
    "/{id}/status",
    status_code=status.HTTP_200_OK,
)
def check_status(id: int, db: Session = Depends(get_db)):
    """Check the clock status of an employee.

    Args:
        id (int): The employee's unique identifier.
        db (Session): Database session for current request.

    Returns:
        dict: Json response with clock status.

    """
    employee = employee_routes.get_employee_by_id(id, db)
    timeclock_services.validate_employee_allowed(employee.allow_clocking)

    if timeclock_repository.check_status(id, db):
        return {"status": "success", "message": "Clocked in"}
    else:
        return {"status": "success", "message": "Clocked out"}


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[TimeclockEntryBase],
)
def get_timeclock_entries(
    start_timestamp: datetime,
    end_timestamp: datetime,
    employee_id: int = None,
    db: Session = Depends(get_db),
):
    """Retrieve all timeclock entries with given time period.

    Args:
        start_timestamp (datetime): The start timestamp for the time period.
        end_timestamp (datetime): The end timestamp for the time period.
        employee_id (int, optional): The employee's unique identifier.
        db (Session): Database session for current request.

    Returns:
        list[TimeclockEntryBase]: The retrieved timeclock entries.

    """
    return timeclock_repository.get_timeclock_entries(
        start_timestamp, end_timestamp, employee_id, db
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
    caller_id: int = Security(
        requires_permission, scopes=["timeclock.update"]
    ),
):
    """Update data for timeclock entry with provided id.

    Args:
        id (int): The timeclock's unique identifier.
        request (TimeclockGroupBase): Request data to update timeclock entry.
        db (Session): Database session for current request.

    Returns:
        TimeclockEntryBase: The updated timeclock entry.

    """
    common_services.validate_ids_match(request.id, id)
    timeclock = timeclock_repository.get_timeclock_entry_by_id(id, db)
    timeclock_services.validate_timeclock_entry_exists(timeclock)

    timeclock_entry = timeclock_repository.update_timeclock_entry_by_id(
        timeclock, request, db
    )
    event_log_routes.create_event_log(
        EventLogBase(
            log=EVENT_LOG_MSGS[IDENTIFIER]["UPDATE"].format(
                timeclock_entry_id=timeclock_entry.id,
            ),
            employee_id=caller_id,
        ),
        db,
    )
    return timeclock_entry


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_timeclock_by_id(
    id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["timeclock.delete"]
    ),
):
    """Delete timeclock data with provided id.

    Args:
        id (int): The timeclock's unique identifier.
        db (Session): Database session for current request.

    """
    timeclock_entry = timeclock_repository.get_timeclock_entry_by_id(id, db)
    timeclock_services.validate_timeclock_entry_exists(timeclock_entry)

    timeclock_repository.delete_timeclock_entry(timeclock_entry, db)
    event_log_routes.create_event_log(
        EventLogBase(
            log=EVENT_LOG_MSGS[IDENTIFIER]["DELETE"].format(
                timeclock_entry_id=timeclock_entry.id,
            ),
            employee_id=caller_id,
        ),
        db,
    )
