"""Module providing the business logic for event log-related operations."""

from fastapi import HTTPException, status
from src.event_log.constants import EXC_MSG_EVENT_LOG_ENTRY_NOT_FOUND
from src.event_log.models import EventLog


def validate_event_log_exists(
    event_log: EventLog | None,
) -> bool:
    """Validates whether a event log exists.

    Args:
        event_log (EventLog | None): The event log to validate.

    Raises:
        HTTPException (404): If the event log does not exist.

    Returns:
        bool: True if the event log exists.

    """
    if not event_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=EXC_MSG_EVENT_LOG_ENTRY_NOT_FOUND,
        )
    return True
