"""Module defining API for event log-related operations."""

from datetime import datetime

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.orm import Session

import src.event_log.repository as event_log_repository
import src.user.routes as user_routes
from src.database import get_db
from src.event_log.constants import BASE_URL, EXC_MSG_EVENT_LOG_ENTRY_NOT_FOUND
from src.event_log.schemas import EventLogBase, EventLogExtended
from src.services import requires_permission, validate

router = APIRouter(prefix=BASE_URL, tags=["event_log"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=EventLogExtended,
)
def create_event_log(
    request: EventLogBase,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["event_log.create"]
    ),
):
    """Insert new event log data.

    Args:
        request (EventLogBase): Request data for new event log.
        db (Session): Database session for current request.

    Returns:
        EventLogExtended: The created event log entry.

    """
    user_routes.get_user_by_id(request.user_id, db)
    return event_log_repository.create_event_log(request, db)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[EventLogExtended],
)
def get_event_log_entries(
    start_timestamp: datetime,
    end_timestamp: datetime,
    user_id: int = None,
    log_filter: str = None,
    db: Session = Depends(get_db),
    caller_id: int = Security(requires_permission, scopes=["event_log.read"]),
):
    """Retrieve all event logs with given time period.
    If user_id is provided, it will be used to filter the logs to
        those associated with the id.
    If log_filter is provided, it will be used to filter the logs to those
        containing the filter text.

    Args:
        start_timestamp (datetime): The start timestamp for the time period.
        end_timestamp (datetime): The end timestamp for the time period.
        user_id (int, optional): User's unique identifier.
            Defaults to None.
        log_filter (str, optional): Filter for log messages.
            Defaults to None.
        db (Session): Database session for current request.

    Returns:
        list[EventLogExtended]: The retrieved event log entries.

    """
    return event_log_repository.get_event_log_entries(
        start_timestamp, end_timestamp, user_id, log_filter, db
    )


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=EventLogExtended,
)
def get_event_log_by_id(
    id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(requires_permission, scopes=["event_log.read"]),
):
    """Retrieve event log data with provided id.

    Args:
        id (int): Event log's unique identifier.
        db (Session): Database session for current request.

    Returns:
        EventLogExtended: The retrieved event log entry.

    """
    event_log = event_log_repository.get_event_log_by_id(id, db)
    validate(
        event_log,
        EXC_MSG_EVENT_LOG_ENTRY_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    return event_log


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_event_log_by_id(
    id: int,
    db: Session = Depends(get_db),
    caller_id: int = Security(
        requires_permission, scopes=["event_log.delete"]
    ),
):
    """Delete event log data with provided id.

    Args:
        id (int): Event log's unique identifier.
        db (Session): Database session for current request.

    """
    event_log = event_log_repository.get_event_log_by_id(id, db)
    validate(
        event_log,
        EXC_MSG_EVENT_LOG_ENTRY_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    event_log_repository.delete_event_log_entry(event_log, db)
