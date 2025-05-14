"""Module defining API for event log-related operations."""

from datetime import datetime
from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.event_log.constants import BASE_URL
import src.event_log.repository as event_log_repository
import src.event_log.services as event_log_services
from src.event_log.schemas import EventLogBase, EventLogExtended
import src.employee.routes as employee_routes

router = APIRouter(prefix=BASE_URL, tags=["event_log"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=EventLogExtended,
)
def create_event_log(request: EventLogBase, db: Session = Depends(get_db)):
    """Insert new event log data.

    Args:
        request (EventLogBase): Request data for new event log.
        db (Session): Database session for current request.

    Returns:
        EventLogExtended: Response containing newly created event log data.

    """
    employee_routes.get_employee_by_id(request.employee_id, db)
    return event_log_repository.create_event_log(request, db)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[EventLogExtended],
)
def get_event_log_entries(
    start_timestamp: datetime,
    end_timestamp: datetime,
    employee_id: int = None,
    log_filter: str = None,
    db: Session = Depends(get_db),
):
    """Retrieve all event logs with given time period.
    If employee_id is provided, it will be used to filter the logs to those
        associated with the ID.
    If log_filter is provided, it will be used to filter the logs to those
        containing the filter text.

    Args:
        start_timestamp (datetime): The start timestamp for the time period.
        end_timestamp (datetime): The end timestamp for the time period.
        employee_id (int, optional): ID of the employee associated with the
            event. Defaults to None.
        log_filter (str, optional): Filter for log messages. Defaults to None.
        db (Session): Database session for current request.

    Returns:
        list[EventLogExtended]: The retrieved event log entries.

    """
    return event_log_repository.get_event_log_entries(
        start_timestamp, end_timestamp, employee_id, log_filter, db
    )


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=EventLogExtended,
)
def get_event_log_by_id(id: int, db: Session = Depends(get_db)):
    """Retrieve event log data with provided id.

    Args:
        id (int): The event_log's unique identifier.
        db (Session): Database session for current request.

    Returns:
        EventLogExtended: The retrieved event log entry.

    """
    event_log = event_log_repository.get_event_log_by_id(id, db)
    event_log_services.validate_event_log_exists(event_log)

    return event_log


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_event_log_by_id(id: int, db: Session = Depends(get_db)):
    """Delete event_log data with provided id.

    Args:
        id (int): The event_log's unique identifier.
        db (Session): Database session for current request.

    """
    event_log = event_log_repository.get_event_log_by_id(id, db)
    event_log_services.validate_event_log_exists(event_log)

    event_log_repository.delete_event_log_entry(event_log, db)
