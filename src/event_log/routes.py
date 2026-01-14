"""Module defining API for event log-related operations."""

from datetime import datetime

from fastapi import APIRouter, Depends, Security, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.event_log.constants import BASE_URL, EXC_MSG_EVENT_LOG_ENTRY_NOT_FOUND
from src.event_log.repository import (
    create_event_log as create_event_log_in_db,
    delete_event_log_entry,
    filter_logs_by_permissions,
    get_event_log_by_id,
    get_event_log_entries,
)
from src.event_log.schemas import EventLogBase, EventLogExtended
from src.services import requires_permission, validate
from src.user.repository import get_user_by_badge_number

router = APIRouter(prefix=BASE_URL, tags=["event_log"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=EventLogExtended,
)
def create_event_log(
    request: EventLogBase,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
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
    get_user_by_badge_number(request.badge_number, db)
    return create_event_log_in_db(request, db)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[EventLogExtended],
)
def get_event_log_entries(
    start_timestamp: datetime,
    end_timestamp: datetime,
    badge_number: str = None,
    log_filter: str = None,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["event_log.read"]
    ),
):
    """Retrieve all event logs with given time period.
    Logs are filtered based on the caller's permissions - only logs for
        entities the caller has read access to will be returned.
    If badge_number is provided, it will be used to filter the logs to
        those associated with the badge number.
    If log_filter is provided, it will be used to filter the logs to those
        containing the filter text.

    Args:
        start_timestamp (datetime): The start timestamp for the time period.
        end_timestamp (datetime): The end timestamp for the time period.
        badge_number (int, optional): User's badge number.
            Defaults to None.
        log_filter (str, optional): Filter for log messages.
            Defaults to None.
        db (Session): Database session for current request.
        caller_badge (str): The badge number of the user making the request.

    Returns:
        list[EventLogExtended]: The retrieved event log entries.

    """
    # Get the caller's user object to check permissions
    caller_user = get_user_by_badge_number(caller_badge, db)

    # Get all event logs matching the criteria
    all_logs = get_event_log_entries(
        start_timestamp, end_timestamp, badge_number, log_filter, db
    )

    # Filter logs based on caller's permissions
    filtered_logs = filter_logs_by_permissions(all_logs, caller_user, db)

    return filtered_logs


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=EventLogExtended,
)
def get_event_log_by_id(
    id: int,
    db: Session = Depends(get_db),
    caller_badge: str = Security(
        requires_permission, scopes=["event_log.read"]
    ),
):
    """Retrieve event log data with provided id.

    Args:
        id (int): Event log's unique identifier.
        db (Session): Database session for current request.

    Returns:
        EventLogExtended: The retrieved event log entry.

    """
    event_log = get_event_log_by_id(id, db)
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
    caller_badge: str = Security(
        requires_permission, scopes=["event_log.delete"]
    ),
):
    """Delete event log data with provided id.

    Args:
        id (int): Event log's unique identifier.
        db (Session): Database session for current request.

    """
    event_log = get_event_log_by_id(id, db)
    validate(
        event_log,
        EXC_MSG_EVENT_LOG_ENTRY_NOT_FOUND,
        status.HTTP_404_NOT_FOUND,
    )

    delete_event_log_entry(event_log, db)
